from cProfile import run
import threading
import json
import time
import random

from cloudpss.utils.graphqlUtil import graphql_request
from .receiver import Receiver
from .MessageStreamReceiver import MessageStreamReceiver
from .result import IESLabSimulationResult, PowerFlowResult, EMTResult, Result, IESResult
from .IESLabPlanResult import IESLabPlanResult
from .IESLabEvaluationResult import IESLabEvaluationResult
from .IESLabTypicalDayResult import IESLabTypicalDayResult
from .storage import Storage
from ..utils import request
from typing import TypeVar, Generic
import re

RECEIVER = {
    'default': MessageStreamReceiver,
}
T = TypeVar('T', Result, EMTResult, PowerFlowResult, IESResult,
            IESLabSimulationResult, IESLabPlanResult, IESLabEvaluationResult,
            IESLabTypicalDayResult)

IES_LAB_RESULT = {
    'function/ieslab/plan': IESLabPlanResult,
    'function/ieslab/evaluation': IESLabEvaluationResult
}
RESULT_DB = {
    'job-definition/cloudpss/emtp': EMTResult,
    'job-definition/cloudpss/emtps': EMTResult,
    'job-definition/cloudpss/sfemt': EMTResult,
    'job-definition/cloudpss/power-flow': PowerFlowResult,
    'job-definition/cloudpss/ies-simulation': IESResult,
    'job-definition/cloudpss/ies-optimization': IESResult,
    'job-definition/cloudpss/three-phase-powerFlow': PowerFlowResult,
    'job-definition/ies/ies-simulation': IESLabSimulationResult,
    'job-definition/ies/ies-gmm': IESLabTypicalDayResult,
    'job-definition/cloudpss/ieslab-simulation': IESLabSimulationResult,
    'job-definition/cloudpss/ieslab-gmm': IESLabTypicalDayResult,
}


class Runner(Generic[T]):

    def __init__(self, id,taskId, name, job, config, revision, modelRid, policy,
                 **kwargs):
        self.id = id
        self.taskId = taskId
        self.db = Storage(taskId, name, job, config, revision, modelRid)
        result = RESULT_DB.get(job['rid'], Result)
        self.result: T = result(self.db)  # type: ignore
        self.receiver = kwargs.get('receiver', None)

    def __listenStatus(self):
        if self.receiver is None:
            return False
        if self.receiver.status() == -1:
            raise Exception(self.receiver.error)
        return self.receiver.isOpen

    def status(self):
        """
        运行状态
        :return: 运行状态  0/1/-1 1 表示正常结束，0 表示运行中， -1 表示数据接收异常


        >>>> runner.status()  
        """
        if self.receiver is None:
            raise Exception('not find receiver')
        return self.receiver.status()

    def __listen(self, **kwargs):

        receiver = kwargs.get('RECEIVER', 'default')
        receiverclass = None
        if type(receiver) is str:
            if receiver not in RECEIVER:
                receiverclass = RECEIVER['default']
            else:
                receiverclass = RECEIVER[receiver]
        if receiverclass is None:
            raise Exception('not find receiver')
        self.receiver = receiverclass(self.taskId, self.db, **kwargs)
        self.receiver.connect()

    def terminate(self):
        """
        结束当前运行的算例

        """
        self.abort(0)
    
    def abort(self,timeout=3):
        """
        结束当前运行的算例

        """
        query = '''mutation ($input: AbortJobInput!) {
            job: abortJob(input: $input) {
                id
                status
            }
        }
        '''
        variables = {
            'input': {
                'id': self.taskId,
                'timeout': timeout
            }
        }
        graphql_request(query, variables)


    @staticmethod
    def create(revisionHash,
               job,
               config,
               name=None,
               rid='',
               policy=None,
               **kwargs):
        '''
            创建一个运行任务

            :params: revision 项目版本号
            :params: job 调用仿真时使用的计算方案，为空时使用项目的第一个计算方案
            :params: config 调用仿真时使用的参数方案，为空时使用项目的第一个参数方案
            :params: name 任务名称，为空时使用项目的参数方案名称和计算方案名称
            :params: rid 项目rid，可为空

            :return: 返回一个运行实例

            >>> runner = Runner.runRevision(revision,job,config,'')
        '''

        #处理policy字段
        if policy is None:
            policy = {}
            if policy.get('tres', None) is None:
                policy['tres'] = {}
            policy['queue'] = job['args'].get('@queue', 1)
            policy['priority'] = job['args'].get('@priority', 0)
            tres = {'cpu': 1, 'ecpu': 0, 'mem': 0}
            tresStr = job['args'].get('@tres', '')
            for t in re.split('\s+', tresStr):
                if t == '':
                    continue
                k, v = t.split('=')
                tres[k] = float(v)  #type: ignore
            policy['tres'] = tres

        query = '''mutation($input:CreateJobInput!){job:createJob(input:$input){id input output status position}}'''
        function = job['rid'].replace('job-definition/cloudpss/',
                                      'function/CloudPSS/')
        variables = {
            'input': {
                "args":
                {
                    **job['args'],
                    '_ModelRevision' : revisionHash,
                    '_ModelArgs' : config['args']
                },
                "context": [
                    function,
                    f"model/@sdk/{str(int(time.time() * random.random()))}"
                ],
                "policy":
                policy,
            }
        }
        r = graphql_request(query, variables)
        if 'errors' in r:
            raise Exception(r['errors'])
        messageId = r['data']['job']['output']
        id = r['data']['job']['id']
        runner = Runner(id,messageId, name, job, config, revisionHash, rid,
                        policy, **kwargs)

        event = threading.Event()
        thread = threading.Thread(target=runner.__listen, kwargs=kwargs)
        thread.setDaemon(True)
        thread.start()

        while not runner.__listenStatus():
            time.sleep(0.1)

        return runner

    

class HttpRunner(Runner[T]):

    def __init__(self, job, simulationId, **kwargs):
        self.simulationId = simulationId
        self.job = job
        self.__taskId = self.__getLastTask()
        result = IES_LAB_RESULT.get(job.get('rid', ''), IESLabPlanResult)
        self.result: T = result(self.simulationId, self.__taskId,
                                **kwargs)  # type: ignore

    def __getLastTask(self):
        r = request('GET',
                    'api/ieslab-plan/taskmanager/getSimuLastTasks',
                    params={'simuid': self.simulationId})
        result = json.loads(r.text)
        return result['data'].get('task_id', None)

    def status(self):
        if self.__taskId is None:
            return False
        return self.result.status()  # type: ignore
        pass