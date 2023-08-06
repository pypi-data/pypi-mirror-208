import datetime
import os

from loguru import logger
from common.db.handle_db import MysqlDB
from common.data.handle_common import get_system_key,format_caseName
from common.common.constant import Constant
from common.plat.jira_platform import JiraPlatForm
from common.data.data_process import DataProcess


class MysqlPlatForm(object):
    @classmethod
    def sync_autotest_script(self, testname, caseid, caseurl):
        if DataProcess.isNotNull(get_system_key(Constant.GIT_PROJECTNAME)):
            testname, gitname, scripturl, scriptclass, scriptmethod, scriptname = DataProcess.getCaseUrlMeta(testname,
                                                                                                             caseurl)
            if DataProcess.isNotNull(scripturl):
                if caseid != '00000':
                    JiraPlatForm.updateDescription(caseid, scripturl)
                    JiraPlatForm.updateTestReference(caseid, caseurl)
                traffic = get_system_key('ATFDB')
                env =get_system_key('ATFEVN')
                _config = {'key': 'traffic', 'env': 'test'}
                _mysql = MysqlDB(_config)
                sql = f"delete from test_autotest_script where testname='{testname}' and gitname='{gitname}'"
                _list = _mysql.execute(sql)
                _mysql.conn.commit()
                _date = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                _sql = f"INSERT INTO `traffic_test`.`test_autotest_script`(`gitname`, `suitname`, `tagversion`, `testid`, `testname`, `scriptclass`, `scriptmethod`, `scriptname`, `scriptpackage`, `status`, `updatetime`, `caseurl`, `scripturl`) " \
                       f"VALUES ('{gitname}', '', 'run', '{caseid}', '{testname}', '{scriptclass}', '{scriptmethod}', '{scriptname}', '', '0', '{_date}', '{caseurl}', '{scripturl}')"
                _mysql.execute(_sql)
                _mysql.conn.commit()
                _mysql.close()
                logger.info(f'保存用例和脚本关系成功：用例名称:{testname} 脚本路径:{caseurl}')

    @classmethod
    def insert_api_data(self, _url, _methond, _header, _data, _reponse_time,_reponse_code):
        _hash = hash(f'{_url}:{_methond}:{_header}:{_data}:{_reponse_time}')
        _data= str(_data).replace("'","")
        _config = {'key':'atf'}
        _date = datetime.datetime.now()
        _project_alice = os.environ['ProjectAlice']
        _sql=f"INSERT INTO `traffic_test`.`base_api_data`(`hash_id`,`project_alice`, `url`,`method`, `data`, `reponse_time`,`reponse_code`, `create_time`) VALUES ('{_hash}','{_project_alice}', '{_url}', '{_methond}', '{_data}', '{_reponse_time}', '{_reponse_code}','{_date}')"
        _mysql = MysqlDB(_config)
        _mysql.execute(_sql)
        _mysql.conn.commit()
        _mysql.close()

    @classmethod
    def getScriptyPathByCaseNameList(self, CaseNameList):
        _config = {'key':'atf'}
        _mysql = MysqlDB(_config)
        sql = f"select distinct(caseurl) from test_autotest_script where `status` = '0'"
        sql += " and testname in (%s)" % ','.join(["'%s'" % testname for testname in CaseNameList])
        _list = _mysql.execute(sql).fetchall()
        _mysql.close()
        return _list


    @classmethod
    def get_test_autotest_run(self, jirakey, cycleId, result:str="'通过','未执行','失败','自动化执行'"):
        _info = []
        _sql = f"select * from `traffic_test`.`test_autotest_run` where jirakey='{jirakey}' and cycleId='{cycleId}' and status in ({result})"
        try:
            _config = {'key':'atf'}
            _mysql = MysqlDB(_config)
            _info = _mysql.execute(_sql).fetchall()
            return _info
        except Exception as e:
            logger.error(f'查询SQL异常：{_sql}')
            return _info

    @classmethod
    def sync_projectConfig(self, gitName):
        _info = []
        _sql = f"select count(*) as _count from `traffic_test`.`test_autotest_script` where gitname='{gitName}'"
        try:
            _config = {'key': 'atf'}
            _mysql = MysqlDB(_config)
            _info = _mysql.execute(_sql).fetchall()
            _sql = f"update `traffic_test`.`system_global_conf` set `case_count`={_info[0]['_count']} where git_project_name='{gitName}'"
            _mysql = MysqlDB(_config)
            _mysql.execute(_sql)
            _mysql.conn.commit()
            return _info
        except Exception as e:
            logger.error(f'查询SQL异常：{_sql}')
            return _info

    @classmethod
    def get_test_case_info(self, jirakey, cycleId, caseName):
        _config = {'key':'atf'}
        _sql = f"select * from `traffic_test`.`test_autotest_run` where jirakey='{jirakey}' and cycleId='{cycleId}' and casename='{caseName}'"
        _mysql = MysqlDB(_config)
        _info = _mysql.execute(_sql).fetchall()
        return _info

    @classmethod
    def get_test_case_info_ByID(self, jirakey, cycleId, caseid):
        _config = {'key':'atf'}
        _sql = f"select * from `traffic_test`.`test_autotest_run` where jirakey='{jirakey}' and cycleId='{cycleId}' and caseid='{caseid}'"
        _mysql = MysqlDB(_config)
        _info = _mysql.execute(_sql).fetchall()
        return _info


    @classmethod
    def get_api_data(self, _url, _methond, _header, _data, _reponse_time, _reponse_code):
        _config = {'key':'atf'}
        _sql = f"select * from `traffic_test`.`base_api_data` where `url`='{_url}' and `method`='{_methond}' and `data`='{_data}' and `reponse_code`={_reponse_code} "
        _mysql = MysqlDB(_config)
        _time=''
        _info=''
        for _temp in  _mysql.execute(_sql).fetchall():
            _time=str(_temp['reponse_time'])+"S, "+_time
            _info =str(_temp['create_time']) +"执行时间:"+str(_temp['reponse_time']) + "S, " + _info
        return _time,_info








