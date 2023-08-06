class Constant(object):
    #重要的
    P0 = 'critical'
    #正常用例
    P1 = 'normal'
    #不太重要
    P2 = 'minor'
    #不重要
    P3 = 'trivial'

    PROD = '生产数据'

    TEST_DATA_PARAMETER = '用例属性参数化'

    #执行状态
    STATUS_PRE = "准备执行"
    STATUS_AUTOTEST = "自动化执行"
    STATUS_SKIP = "跳过"
    STATUS_PASS = "通过"
    STATUS_FAIL = "失败"
    STATUS_NOTEST = "未执行"

    #用例类型
    CASE_RUN_TYPE = "CaseRunType"
    CASE_TYPE_AUTO = "自动化"
    CASE_TYPE_Man = "手工"

    #配置
    ENV = 'env'
    Jenkins_RESULT = 'Result'
    PROJECT_NAME = 'projectname'
    PROJECT_ALICE = 'ProjectAlice'
    PORJECT_ID = 'projectId'
    ISSUE_KEY = 'issueKey'
    TEST_TYPE = 'type'
    PASS_RATE = 'passrate'
    CURRENT_PATH = 'currentpath'
    TEST_CASE_PATH = 'TestCasePath'
    TEST_CASE_MARK = 'TestCaseMark'
    TEST_SRTCYCLE_ID = 'SRTCYCLE'
    TEST_RUN_THREAD = 'thread'
    TEST_TestPlan_ID = 'TESTPLANID'
    TEST_TestPlan_NAME = 'TESTPLANNAME'
    TEST_TestPlan_URL = 'TESTPLANURL'
    TEST_SRTCYCLE_NAME = 'CycleName'
    TEST_SRTCYCLE_URL = 'CycleURL'
    TEST_CASE_NAME_LIST = 'TestCaseNameList'
    TEST_SUIT_NAME_LIST ='TestSuitNameList'
    GIT_PROJECTNAME = 'gitProjectName'
    ALLURE_PATH = 'AllurePath'
    RUN_TYPE = 'RuntType'
    Data_init = 'DATAINIT'
    RUN_TYPE_JENKINS = 'jenkins'
    CASE_NAME_RUN_FIX = 'CASENAMERUNID'
    CASE_NAME_NO_FIX ='CASENAMEID'



    SEND_URSER_LIST = 'toUser'

    #未查找到内容
    DATA_NO_CONTENT = '在DataBus中未提取到内容!!!'
    RESPONSE_CODE = 'responseCode'
    DATA_TYPE = 'DATATYPE'
    DATA_LIST = 'LIST'
    DATA_DIC = 'DIC'

    #用例相关Meta
    CASE_NO = '用例编号'
    CASE_MODEL = '所属模块'
    CASE_TITLE = '用例标题'
    CASE_STORY_NO = '需求编号'
    CASE_STORY= '需求名称'
    CASE_LINK= '需求链接'
    CASE_PRIORITY = '优先级'
    CASE_STATUS = '是否执行'
    CASE_DATA = '请求数据'
    CASE_DATA_TYPE = '数据类型'
    CASE_DATA_HEADER = '请求头'
    CASE_DATA_PARAM = '入参类型'
    CASE_DATA_METHOD = '请求方式'
    CASE_EXPECTED = '预期结果'


    #数据类型：
    DATA_TYPE_JSON = 'json'
    DATA_TYPE_TEXT = 'text'
    DATA_TYPE_XML = 'xml'

    #Header类型：
    HEADER_CONTENT_TYPE_JSON = '$.common.request_headers_json'
    HEADER_CONTENT_TYPE_XML =  '$.common.request_headers_xml'
    HEADER_CONTENT_TYPE_TEXT = '$.common.request_headers_text'
    HEADER_CONTENT_TYPE_DATA = '$.common.request_headers_data'
    HEADER_CONTENT_TYPE_FORM = '$.common.request_headers_form'


    #Jira配置：
    JIRA_URL = 'http://jira.ceair.com:8080'
    #测试
    #JIRA_URL = 'http://10.18.19.159:8080'
    JIRA_USERNAME = 'jiraUserName'
    JIRA_PASSWORD = 'jiraPassword'

    # Jenkis Deploy配置：
    JENKINS_DEPLOY = 'jenkinsDeloyURL'
    JENKINS_DEPLOY_USER = 'jenkinsDeloyUser'
    JENKINS_DEPLOY_TOKEN= 'jenkinsDeloyPassword'

    #msg配置
    MSG_URL = 'msgapi'
    MSG_TOKEN= 'msgtoken'
    MSG_id = 'msgid'

    # ATF配置：
    ATF_URL_API='http://10.18.20.175:9999/api'
    ATF_URL = 'http://10.18.20.175:9999'
    ATF_API = 'http://10.18.20.175:9996/autotest/api'

    #Python服务配置
    ATF_PYTHON_URL = 'http://10.18.20.175:5000'

    #浏览器类型
    USER_AGENTS = [
        "Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2228.0 Safari/537.36",
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2227.0 Safari/537.36",
    ]





