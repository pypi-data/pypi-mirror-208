import json
from jsonpath import jsonpath

from common.common.api_driver import APIDriver
from common.data.handle_common import get_system_key, set_system_key
from common.common.constant import Constant
from requests.auth import HTTPBasicAuth
from common.data.data_process import DataProcess
from loguru import logger

class JiraPlatForm(object):


    @classmethod
    def getJiraIssueInfo(self, jira_no):
        """
        通过Jira号获取jira信息
        :param jira_no:
        :return:
        """

        return APIDriver.http_request(url=f"{Constant.JIRA_URL}/rest/api/latest/issue/{jira_no}",method='get',
                                        _auth=HTTPBasicAuth(get_system_key(Constant.JIRA_USERNAME),get_system_key(Constant.JIRA_PASSWORD))
                                      )


    @classmethod
    def setJiraFlowStatus(self, flow_id):
        """
                触发工作流程
                :param jira_key: Jira_key
                :param flow_id: 流程ID
                :return:
                """
        if DataProcess.isNotNull(get_system_key(Constant.ISSUE_KEY)):
            jira_key =get_system_key(Constant.ISSUE_KEY)
            logger.info(f'更新{jira_key}工作流状态')
            return APIDriver.http_request(url=f"{Constant.JIRA_URL}/rest/api/2/issue/{jira_key}/transitions?expand=transitions.fields",
                                          method='post',
                                          parametric_key='json',
                                          data=json.loads('{"transition":{"id":"flow_id"}}'.replace('flow_id',flow_id)),
                                          _auth=HTTPBasicAuth(get_system_key(Constant.JIRA_USERNAME),
                                                              get_system_key(Constant.JIRA_PASSWORD))
                                          )
        else:
            return "no issue key"

    @classmethod
    def setJiraComment(self, comment):
        """
        添加Jira的备注
        :param jira_key:
        :param comment:
        :return:
        """
        if DataProcess.isNotNull(get_system_key(Constant.ISSUE_KEY)):
            jira_key = get_system_key(Constant.ISSUE_KEY)
            return APIDriver.http_request(url=f"{Constant.JIRA_URL}/rest/api/2/issue/{jira_key}/comment",
                                          method='post',
                                          parametric_key='json',
                                          data=json.loads('{"body":"comment"}'.replace('comment',comment)),
                                          _auth=HTTPBasicAuth(get_system_key(Constant.JIRA_USERNAME),
                                                            get_system_key(Constant.JIRA_PASSWORD))
                                         )
        else:
            return "no issue key"


    @classmethod
    def _isNotNull(self, data):
        try:
            if data is None:
                return False
            if isinstance(data, str):
                _data = data
            else:
                _data = str(data)
            if _data.strip() == '':
                return False
            else:
                return True
        except Exception as e:
            logger.info('判断数据是否为空异常,数据：' + data)
            return True



    @classmethod
    def updateTestReference(self,testCaseIssueKey, desc):
        try:
            if JiraPlatForm.getTestReference(testCaseIssueKey) != desc.strip():
               APIDriver.http_request(
                    url=f"{Constant.JIRA_URL}/rest/synapse/latest/public/testCase/{testCaseIssueKey}/updateTestReference",
                    method='post',
                    parametric_key='json',
                    data={
                        "automationReference": f"{desc}"
                    },
                    _auth=HTTPBasicAuth(get_system_key(Constant.JIRA_USERNAME), get_system_key(Constant.JIRA_PASSWORD))
                )
        except Exception as e:
            logger.info(f' 用例Key:{testCaseIssueKey} 自动化引用信息:{desc} 更新用例描述异常:{e}')

    @classmethod
    def getTestReference(self, testCaseIssueKey):
        automationReference = ""
        try:
            response = APIDriver.http_request(
                url=f"{Constant.JIRA_URL}/rest/synapse/latest/public/testCase/{testCaseIssueKey}/automationReference",
                method='get',
                _auth=HTTPBasicAuth(get_system_key(Constant.JIRA_USERNAME), get_system_key(Constant.JIRA_PASSWORD))
            )
            automationReference = json.loads(response.content)['automationReference']
            return automationReference
        except Exception as e:
            logger.info(f' 用例Key:{testCaseIssueKey}  获取用例引用异常:{e}')
            return automationReference

    @classmethod
    def updateDescription(self,testCaseIssueKey, desc):
        try:
            case_desc = json.loads(JiraPlatForm.getJiraIssueInfo(testCaseIssueKey + '?fields=description').content)['fields']['description']
            if DataProcess.isNotNull(case_desc) == False or str(case_desc).strip() != desc.strip():
                APIDriver.http_request(
                    url=f"{Constant.JIRA_URL}/rest/api/2/issue/{testCaseIssueKey}",
                    method='put',
                    parametric_key='json',
                    data={"fields" : {"description": f"{desc}","customfield_14903":{"value":"自动化"}}},
                    _auth=HTTPBasicAuth(get_system_key(Constant.JIRA_USERNAME), get_system_key(Constant.JIRA_PASSWORD))
                )
        except Exception as e:
            logger.info(f' 用例Key:{testCaseIssueKey} 描述信息:{desc} 更新用例描述异常:{e}')

    @classmethod
    def getDataByJql(self, jql, fields):
        content = list()
        try:
            content = APIDriver.http_request(
                url=f"{Constant.JIRA_URL}/rest/api/2/search",
                method='post',
                parametric_key='json',
                data={
                    "jql": jql,
                    "startAt": 0,
                    "maxResults": 1000,
                    "fields": fields
                },
                _auth=HTTPBasicAuth(get_system_key(Constant.JIRA_USERNAME), get_system_key(Constant.JIRA_PASSWORD))
            )
            content = json.loads(content.content)
            return content
        except Exception as e:
            logger.info(f'查询Jql异常：{jql}')
            return content

    @classmethod
    def saveCaseToTestPlan(self,testPlanIssueKey,jiraKey):
        content = list()
        try:
            content = APIDriver.http_request(
                url=f"{Constant.JIRA_URL}/rest/synapse/latest/public/testPlan/{testPlanIssueKey}/addMembers",
                method='post',
                parametric_key='json',
                data={
                    "testCaseKeys": jiraKey
                },
                _auth=HTTPBasicAuth(get_system_key(Constant.JIRA_USERNAME), get_system_key(Constant.JIRA_PASSWORD))
            )
            content = json.loads(content.content)
            return content
        except Exception as e:
            logger.info(f'添加测试用例到测试计划异常：{jql}')
            return content

    @classmethod
    def saveCaseToTestPlanByJql(self, testPlanIssueKey, jql):
        content = JiraPlatForm.getDataByJql(jql,["id", "key"])
        keys = jsonpath(content, "$.issues[*].key")
        logger.info(f'添加用例列表：'+str(keys))
        JiraPlatForm.saveCaseToTestPlan(testPlanIssueKey, keys)
        logger.info(f'提交到测试计划：' + str(testPlanIssueKey)+'成功')

