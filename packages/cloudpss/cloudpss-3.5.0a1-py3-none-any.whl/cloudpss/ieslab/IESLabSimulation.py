import json
from ..utils import request
from ..model.model import Model
from .DataManageModel import IESSimulationDataManageModel


class IESLabSimulation(object):
    def __init__(self, project={}):
        '''
            初始化
        '''
        self.id = project.get('id', None)
        self.name = project.get('name', None)
        self.__modelRid = project.get('model', None)
        self.project_group = project.get('project_group', None)
        if self.__modelRid is not None:
            self.model = Model.fetch(self.__modelRid)
        self.dataManageModel = IESSimulationDataManageModel(self.id)

    @staticmethod
    def fetch(simulationId):
        '''
            获取算例信息

            :params: simulationId string类型，代表数据项的算例id

            :return: IESLabSimulation
        '''
        try:
            r = request(
                'GET', 'api/ieslab-simulation/rest/simu/{0}/'.format(simulationId))
            project = json.loads(r.text)
            return IESLabSimulation(project)
        except:
            raise Exception('未查询到当前算例')

    def run(self, job=None, name=None):
        '''
            调用仿真 

            :params job:  调用仿真时使用的计算方案，不指定将使用算例保存时选中的计算方案
            :params name:  任务名称，为空时使用项目的参数方案名称和计算方案名称

            :return: 返回一个运行实例
        '''
        if job is None:
            currentJob = self.model.context['currentJob']
            job = self.model.jobs[currentJob]

        job['args']['simulationId'] = self.id
        return self.model.run(job, name=name)

