import json
from math import fabs
from ..utils.httprequests import request


class IESLabPlanResult(object):
    taskId = None

    def __init__(self, simulationId, taskId, **kwargs) -> None:
        """
            初始化
        """
        self.simulationId = simulationId
        # self.__getLastTask()
        self.taskId = taskId
        pass

    # def __getLastTask(self):
    #     r=request('GET','api/ieslab-plan/taskmanager/getSimuLastTasks',params={
    #         'simuid':self.simulationId
    #     })
    #     result= json.loads(r.text)
    #     self.taskId=result['data'].get('task_id',None)
    def status(self):
        '''
            获取运行状态

            :return: boolean 类型
        '''
        log = self.GetLogs()
        for l in log:
            if l['data'] == 'run ends':
                return True
        return False

    def GetLogs(self):
        '''
            获取运行日志

            :return: dict 类型，代表日志信息
        '''
        if self.taskId is None:
            raise Exception('未开始运行')
        r = request('GET',
                    'api/ieslab-plan/taskmanager/getOptimizationLog',
                    params={
                        'simuid': self.simulationId,
                        'taskid': self.taskId
                    })
        result = json.loads(r.text)
        return result['msg']

    def GetPlanNum(self):
        '''
            获取当前result实例对应的优化方案数量
            
            :return: int类型，代表优化方案的数量
        '''
        if self.taskId is None:
            raise Exception('未开始运行')
        r = request('GET',
                    'api/ieslab-plan/taskmanager/getOptimizationResult',
                    params={
                        'simuid': self.simulationId,
                        'taskid': self.taskId,
                        'resultType': 0
                    })
        result = json.loads(r.text)
        return len(result['data'])

    def GetPlanConfiguration(self, planID):
        '''
            获取planID对应的优化方案的配置信息
            
            :param: planID int类型，表示优化方案的ID，数值位于 0~优化方案数量 之间

            :return: dict类型，代表该方案的配置信息，包括每种设备的选型配置、容量配置、成本等相关信息
        '''
        len = self.GetPlanNum()
        if int(planID) > len:
            raise Exception('计算方案id未产生')
        r = request('GET',
                    'api/ieslab-plan/taskmanager/getOptimizationResult',
                    params={
                        'simuid': self.simulationId,
                        'taskid': self.taskId,
                        "planId": planID,
                        'resultType': 1
                    })
        d = json.loads(r.text)
        result = {}
        for val in d['data']:
            result[val['u_name']] = val['data']['data']

        return result

    def GetComponentResult(self, planID, componentID, typicalDayName=''):
        '''
            获取planID对应的优化方案下componentID对应元件的运行信息
            
            :param: planID int 类型，表示优化方案的ID，数值位于 0~优化方案数量 之间
            :param: componentID str 类型，表示元件的标识符
            :param typicalDayName str 类型，代表典型日的名称

            :return: dict类型，代表该元件在不同典型日下的运行信息
        '''
        len = self.GetPlanNum()
        if int(planID) > len:
            raise Exception('计算方案id未产生')
        r = request('GET',
                    'api/ieslab-plan/taskmanager/getOptimizationResult',
                    params={
                        'simuid': self.simulationId,
                        'taskid': self.taskId,
                        'resultType': 3,
                        'typicalDay': typicalDayName,
                        "planId": planID,
                        'u_name': componentID
                    })
        d = json.loads(r.text)
        dict_result = dict()
        for val in d['data']:
            for k, v in val.items():
                dict_result[k] = v
        return dict_result

    def GetComponentTypiDays(self, planId, componentID):
        '''
            获取当前result实例对应的优化方案数量

            :param: planID int 类型，表示优化方案的ID，数值位于 0~优化方案数量 之间
            :param: componentID str 类型，表示元件的标识符
            
            :return: int类型，代表优化方案的数量
        '''
        if self.taskId is None:
            raise Exception('未开始运行')
        r = request('GET',
                    'api/ieslab-plan/taskmanager/getOptimizationResult',
                    params={
                        'simuid': self.simulationId,
                        'taskid': self.taskId,
                        "planId": planId,
                        'u_name': componentID,
                        'resultType': 2
                    })
        result = json.loads(r.text)
        return result['data']
