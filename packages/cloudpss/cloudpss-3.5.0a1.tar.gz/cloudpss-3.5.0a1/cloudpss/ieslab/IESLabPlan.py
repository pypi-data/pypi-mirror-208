import json

from cloudpss.ieslab.DataManageModel import IESPlanDataManageModel
from cloudpss.ieslab.EvaluationModel import IESLabEvaluationModel
from cloudpss.ieslab.PlanModel import IESLabPlanModel
from cloudpss.runner.IESLabTypicalDayResult import IESLabTypicalDayResult
from ..utils import request
from ..model.model import Model
from cloudpss.runner.runner import  Runner

class IESLabPlan(object):
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
        self.dataManageModel = IESPlanDataManageModel(self.id)
        self.planModel = IESLabPlanModel(self.id)
        self.evaluationModel = IESLabEvaluationModel(self.id)

    @staticmethod
    def fetch(simulationId):
        '''
            获取算例信息

            :params: simulationId string类型，代表数据项的算例id

            :return: IESLabPlan
        '''
        try:
            r = request('GET',
                        'api/ieslab-plan/rest/simu/{0}/'.format(simulationId))
            project = json.loads(r.text)
            return IESLabPlan(project)
        except:
            raise Exception('未查询到当前算例')

    def __run(self, job=None, name=None):
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

    def iesLabTypicalDayRun(self, job=None, name=None, **kwargs)->Runner[IESLabTypicalDayResult]:
        '''
            运行典型日计算 

            :params job:  调用仿真时使用的计算方案，不指定将使用算例保存时选中的计算方案
            :params name:  任务名称，为空时使用项目的参数方案名称和计算方案名称

            :return: Runner[IESLabTypicalDayResult]
        '''
        if job is None:
            currentJob = self.model.context['currentJob']
            job = self.model.jobs[currentJob]
            if job['rid'] != 'job-definition/ies/ies-gmm' or job['rid'] != 'job-definition/cloudpss/ieslab-gmm':
                for j in self.model.jobs:
                    if j['rid'] == 'job-definition/ies/ies-gmm' or job['rid'] == 'job-definition/cloudpss/ieslab-gmm':
                        job = j
        if job is None:
            raise Exception("找不到默认的综合能源系统规划典型日生成算法的计算方案")
        if job['rid'] != 'job-definition/ies/ies-gmm'or job['rid'] != 'job-definition/cloudpss/ieslab-gmm':
            raise Exception("不是综合能源系统规划典型日生成算法的计算方案")
        return self.__run(job=job, name=name)

    def iesLabEvaluationRun(self, planId):
        '''
            运行方案评估

            :param planID int类型，表示优化方案的ID，数值位于0~优化方案数量之间

            :return: 方案评估运行实例

        '''
        return self.evaluationModel.run(planId)

    def iesLabEnergyEvaluationRun(self, planId):
        '''
            运行能效评价

            :param planID int类型，表示优化方案的ID，数值位于0~优化方案数量之间

            :return: 能效评价运行实例

        '''
        return self.evaluationModel.EnergyEvaluationRun(planId)

    def iesLabEnvironmentalEvaluationRun(self, planId):
        '''
            运行环保评价

            :param planID int类型，表示优化方案的ID，数值位于0~优化方案数量之间

            :return: 环保评价运行实例
        '''
        return self.evaluationModel.EnvironmentalEvaluationRun(planId)

    def iesLabPlanRun(self):
        '''
            生成方案优选算例

            :return: 方案优选运行实例
        '''
        return self.planModel.run()
