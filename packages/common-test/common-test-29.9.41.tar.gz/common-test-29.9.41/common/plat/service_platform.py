import json
from common.common.constant import Constant
from common.data.handle_common import get_system_key
from common.common.api_driver import APIDriver
from loguru import logger


class ServicePlatForm(object):

    @classmethod
    def sendMsg(self, data):
        try:
            _data = data.encode()
            APIDriver.http_request(url=get_system_key(Constant.MSG_URL), method='post', parametric_key='data',
                                       data=_data)
        except Exception as e:
            logger.info(f'推送Muc:{data} 异常信息' + repr(e))


    @classmethod
    def getCaseByCycle(self, caseName, status, caseId: str = '00000'):
        cycleId = get_system_key(Constant.TEST_SRTCYCLE_ID)
        try:
            response = APIDriver.http_request(url=Constant.ATF_PYTHON_URL+'/jira/cycle/getCase',
                                   method = 'post',
                                   parametric_key = 'json',
                                   data = {"cycleId":cycleId,"caseName":caseName,"caseId":caseId,"status":status},
                                    )
            content = json.loads(response.content)
            return content
        except Exception as e:
            logger.error(f'获取周期编号：{cycleId} 用例名称:{caseName} 用例编号:{caseId} 状态:{status} 异常信息:' + repr(e))


    @classmethod
    def getATFData(self, projectAlice, env):
        try:
            response = APIDriver.http_request(url=Constant.ATF_API + f'/getParam/{projectAlice}/{env}',
                                              method='get',
                                              )
            content = json.loads(response.content)['data']
            return content
        except Exception as e:
            logger.error(f'获取数据项目别名：{projectAlice} 环境:{env}  异常信息' + repr(e))



    @classmethod
    def getTestPlanInfo(self,cycleId):
        return json.loads(APIDriver.http_request(url=f"{Constant.ATF_PYTHON_URL}/jira/plan/get/{cycleId}", method='get').content)


    @classmethod
    def updateByRunid(self, runid, result, comment:str = "", steps:str = ""):
        _dict = {'result': result, 'comment': comment, 'steps': steps}
        APIDriver.http_request(
            url=f"{Constant.ATF_PYTHON_URL}/jira/run/update/{runid}",
            method='post',
            parametric_key='json',
            data=json.loads(json.dumps(_dict,ensure_ascii=False))
        )


    @classmethod
    def syncCycleCase(self, cycleId):
        if self.isNotNull(get_system_key('Result')):
            _dict = {'status': get_system_key('Result')}
        else:
            _dict = {'status': ''}
        APIDriver.http_request(
            url=f"{Constant.ATF_PYTHON_URL}/jira/sync/{cycleId}",
            method='post',
            parametric_key='json',
            data=json.loads(json.dumps(_dict, ensure_ascii=False))
        )


    @classmethod
    def updateStausByCycleId(self, cycleId, status):
        _dict = {'status': status}
        APIDriver.http_request(
            url=f"{Constant.ATF_PYTHON_URL}/jira/update/cycle/status/{cycleId}",
            method='post',
            parametric_key='json',
            data=json.loads(json.dumps(_dict, ensure_ascii=False))
        )


    @classmethod
    def getCaseRunByNameOrID(self, cycleId, name):
        _dict = {'cycleId': cycleId, 'name': name}
        content = APIDriver.http_request(
            url=f"{Constant.ATF_PYTHON_URL}/jira/run/get",
            method='post',
            parametric_key='json',
            data=json.loads(json.dumps(_dict, ensure_ascii=False))
        )
        return json.loads(content.content)


    @classmethod
    def getCaseInfo(self, caseName):
        _dict = {'name': caseName}
        _result = ""
        try:
            if self.isNotNull(get_system_key(Constant.PORJECT_ID)):
                projectId = get_system_key(Constant.PORJECT_ID)
                _dict = {'name': caseName, 'projectId': projectId}
                content = APIDriver.http_request(
                    url=f"{Constant.ATF_PYTHON_URL}/jira/case/get",
                    method='post',
                    parametric_key='json',
                    data=json.loads(json.dumps(_dict, ensure_ascii=False))
                )
            else:
                content = APIDriver.http_request(
                    url=f"{Constant.ATF_PYTHON_URL}/jira/case/get",
                    method='post',
                    parametric_key='json',
                    data=json.loads(json.dumps(_dict, ensure_ascii=False))
                )
            _result = content.content
            return json.loads(_result)
        except Exception as e:
            logger.error(f"获取用例名称:{_dict}  返回内容:{_result} 异常:" + repr(e))

    @classmethod
    def getProjectData(self, projectName, projectKey):
        """
        获取项目数据
        :param projectName: 项目别名
        :param projectKey: 关键词
        :return:
        """

        try:
            content = APIDriver.http_request(url=f"{Constant.ATF_URL}/api/getProjectData/{projectName}/{projectKey}",
            method='get')
            return (json.loads(content.content)["data"]["projectValue"])
        except Exception as e:
            logger.info(f"{Constant.ATF_URL}/api/getProjectData/{projectName}/{projectKey}" + "获取不到value")
            return None

    @classmethod
    def setProjectData(self, projectKey, value, type=1):
        """
        设置项目数据
        :param projectName: 项目别名
        :param projectKey: 关键词
        :param value: 值
        :param type: 数据类型[0可以重复使用，1不可以重复使用]
        :return:
        """
        if get_system_key('ProjectAlice') is not None and get_system_key('ProjectAlice').strip() != '':
            projectName = get_system_key('ProjectAlice')
            return APIDriver.http_request(
                url=f"{Constant.ATF_URL}/api/setProjectData/{projectName}/{projectKey}/{value}/{type}",
                method='get'
            )

    @classmethod
    def runDeploy(self, jobName, _pramater):
        """
        推送测试结果
        :param jobName:
        :param _pramater:
        :return:
        """
        _tempdata = APIDriver.http_request(url=f"{Constant.ATF_URL}/jenkins/runDeploy/{jobName}",
                                           method='get', parametric_key='params', data=_pramater)
        return _tempdata


    @classmethod
    def db_ops(self, _key, _sql, env: str = Constant.ENV):
        """
        执行SQL操作
        :param _key:
        :param _sql:
        :param env:
        :return:
        """
        _sqltemp = _sql.encode("utf-8").decode("latin1")
        if get_system_key(env) is not None:
            env = get_system_key(env)
        sql_type = _sql.strip().split(" ")[0].lower()
        if "select" == sql_type:
            _tempdata = APIDriver.http_request(url=f"{Constant.ATF_URL_API}/querySetResult/{_key}/{env}",
                                               method='post', parametric_key='data', data=_sqltemp
                                               )
            logger.info(f"执行sql成功:{_sql}")
            return list(_tempdata.json())
        if "insert" == sql_type or "delete":
            _tempdata = APIDriver.http_request(url=f"{Constant.ATF_URL_API}/doExecute/{_key}/{env}",
                                               method='post', parametric_key='data', data=_sqltemp)
            logger.info(f"执行sql成功:{_sql}")
            return _tempdata.text
        else:
            logger.error("不支持其他语句类型执行，请检查sql")

    @classmethod
    def isNotNull(self, data):
        try:
            if isinstance(data, bool):
                return data
            if data is None:
                return False
            if isinstance(data, str):
                _data = data
            else:
                _data = str(data)
            if isinstance(data, list):
                if data.__len__() == 0:
                    return False
                else:
                    for temp in data:
                        if self.isNotNull(temp):
                            return True
                    return False
            if _data is None or _data.strip() == '':
                return False
            else:
                return True
        except Exception as e:
            logger.info('判断数据是否为空异常,数据：' + data)
            return True









