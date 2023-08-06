import json
from ..utils.httprequests import request


class IESLabEvaluationResult(object):
    _baseUri = 'api/ieslab-plan/taskmanager/'
    _kindNameMap = {
        "利润与利润分配": "getEconomyResult",
        "财务计划现金": "getFinancialPlanCashFlowResult",
        "资产负债": "getLiabilityAssetsResult",
        "投资使用计划与资金筹措": "getInvestPlanDataResult",
        "借款还本付息计划": "getLoanRepaymentPlanResult",
        "流动资金估算": "getFlowCashEvaluteResult",
        "资产折旧与摊销估算": "getFlowCashEvaluteResult",
        "总成本费用估算表": "getSumCostResult",
        "项目总投资现金流量": "getSumInvestFlowCashResult",
        "项目资本金现金流量": "getProjectCashFlowResult",
        "营业收入、税金、附加和增值税估算": "getIncomeTaxResult",
    }

    def __init__(self, simulationId, taskId=None, **keywords) -> None:
        """
            初始化
        """
        self.simulationId = simulationId
        self.timeId = keywords.get('timeId', 0)
        self.planId = keywords.get('planId', 0)
        self.cmdType = keywords.get('cmdType', None)

    def _fetchItemData(self, url, planID):
        '''
            获取planID对应的优化方案下resultType财务评估结果

            :param planID int 类型，表示优化方案的ID，数值位于0~优化方案数量之间
            :param resultType enum 类型，表示财务评价结果表格的类型

            :return: dict 类型，为源数据的引用，代表方案对应的财务评价基础参数信息
        '''
        r = request('GET',
                    url,
                    params={
                        "simu_id": self.simulationId,
                        "planId": planID,
                        "time": 0
                    })
        data = json.loads(r.text)
        return data

    def status(self):
        '''
            获取运行状态

            :return: boolean 类型
        '''
        result = None
        if self.cmdType is None:
            result = self.GetOverviewResult()
        elif self.cmdType == 'energyEvaluation':
            result = self.GetEnergyEvaluationResult()
        elif self.cmdType == 'environmentalEvaluation':
            result = self.GetEnvironmentalEvaluationResult()
        if result is None:
            return False
        return True

    def GetFinancialResult(self, resultType):
        '''
            获取planID对应的优化方案下resultType财务评估结果

            :param planID int 类型，表示优化方案的ID，数值位于0~优化方案数量之间
            :param resultType enum 类型，表示财务评价结果表格的类型

            :return: dict 类型，为源数据的引用，代表方案对应的财务评价基础参数信息

        '''
        assert (resultType in self._kindNameMap), "数据类型不存在"
        kind = self._kindNameMap.get(resultType, resultType)
        url = self._baseUri + kind
        list = self._fetchItemData(url, self.planId)
        dict_result = dict()
        for val in list['results']:
            for k, v in val.items():
                dict_result[k] = v
        return dict_result['data']

    def GetOverviewResult(self):
        '''
            获取当前结果类对应的优化方案下的概览结果

            :return: array类型，代表该方案对应的概览结果
        '''
        r = request('GET',
                    "api/ieslab-plan/taskmanager/getOverviewResult",
                    params={
                        "simu_id": self.simulationId,
                        "planId": self.planId,
                        "time": self.timeId
                    })
        result = json.loads(r.text)
        if len(result['results']) > 0:
            return result['results'][0]['data']
        return None

    def GetEnergyEvaluationResult(self):
        '''
            获取当前结果类对应的优化方案下的能效评价

            :return: array类型，代表该方案对应的能效评价结果
        '''
        r = request('GET',
                    "api/ieslab-plan/taskmanager/getEnergyEvaluation",
                    params={
                        "simu_id": self.simulationId,
                        "planId": self.planId,
                        "time": self.timeId
                    })
        result = json.loads(r.text)
        if len(result['results']) > 0:
            return result['results'][0]['data']
        return None

    def GetEnvironmentalEvaluationResult(self):
        '''
            获取当前结果类对应的优化方案下的环保评价

            :return: array类型，代表该方案对应的环保评价结果
        '''
        r = request('GET',
                    "api/ieslab-plan/taskmanager/getEnvironmentalEvaluation",
                    params={
                        "simu_id": self.simulationId,
                        "planId": self.planId,
                        "time": self.timeId
                    })
        result = json.loads(r.text)
        if len(result['results']) > 0:
            return result['results'][0]['data']
        return None