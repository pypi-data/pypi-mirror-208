import ast
import json
import xmltodict
import os
import time
from os import path
from loguru import logger
from common.autotest.handle_allure import allure_step
from common.config.config import TEST_FILE_PATH, TEST_DATA_PATH
from common.data.handle_common import req_expr, convert_json,format_caseName,get_system_key
from common.common.constant import Constant
from common.file.ReadFile import get_yaml_config
from jsonschema import validate
from jsonschema.exceptions import SchemaError, ValidationError
from common.db.handle_db import MysqlDB
from common.plat.service_platform import ServicePlatForm


class DataProcess:
    response_dict = {}
    @classmethod
    def save_response(cls, key: str, value: object) -> None:
        """
        保存实际响应
        :param key: 保存字典中的key，一般使用用例编号
        :param value: 保存字典中的value，使用json响应
        """
        cls.response_dict[key] = value
        logger.info(f'添加key: {key}, 对应value: {value}')

    @classmethod
    def xmltoJson(self, xmlstr:str):
        # parse是的xml解析器
        xmlparse = xmltodict.parse(xmlstr)
        # json库dumps()是将dict转化成json格式，loads()是将json转化成dict格式。
        # dumps()方法的ident=1，格式化json
        jsonstr = json.dumps(xmlparse, indent=1)
        return json.loads(jsonstr)

    @classmethod
    def xml_validate(self,result,schema):
        """
        验证XML
        """
        my_schema = xmlschema.XMLSchema(schema)
        return my_schema.is_valid(result)

    @classmethod
    def json_validate(self, result, schema):
        """
        验证JSON
        """
        try:
            validate(instance=result, schema=schema)
        except SchemaError as e:
            return 1, "验证模式schema出错，出错位置：{}，提示信息：{}".format(" --> ".join([i for i in e.path if i]), e.message)
        except ValidationError as e:
            return 1, "不符合schema规定，出错字段：{}，提示信息：{}".format(" --> ".join([i for i in e.path if i]), e.message)
        else:
            return 0, 'success'

    @classmethod
    def handle_path(cls, path_str: str) -> str:
        """路径参数处理
        :param path_str: 带提取表达式的字符串 /&$.case_005.data.id&/state/&$.case_005.data.create_time&
        上述内容表示，从响应字典中提取到case_005字典里data字典里id的值，假设是500，后面&$.case_005.data.create_time& 类似，最终提取结果
        return  /511/state/1605711095
        """
        # /&$.case.data.id&/state/&$.case_005.data.create_time&
        return req_expr(path_str, cls.response_dict)

    @classmethod
    def handle_header(cls, token) -> dict:
        """处理header
        :param token: 写： 写入token到header中， 读： 使用带token的header， 空：使用不带token的header
        return
        """
        if token == 'None':
            return None
        if token == '空':
            return ''
        if token is None or str(token) == '':
            header = get_yaml_config('$.common.request_headers')
        else:
            if isinstance(token, str) and token.find('$.common') != -1:
                header = get_yaml_config(token)
            else:
                header = token
        if token == '读':
            header = cls.handle_data_fromat(header.copy())
        else:
            header = cls.handle_data_fromat(header)
        if isinstance(header, dict):
            return header
        else:
            return ast.literal_eval(header)

    @classmethod
    def handler_files(cls, file_obj: str) -> object:
        """file对象处理方法
        :param file_obj: 上传文件使用，格式：接口中文件参数的名称:"文件路径地址"/["文件地址1", "文件地址2"]
        实例- 单个文件: &file&D:
        """
        d = path.dirname(__file__)
        # 返回当前d文件的父目录地址
        parent_path = os.path.dirname(d)

        if file_obj == '' or file_obj is None:
            return
        for k, v in convert_json(file_obj).items():
            # 多文件上传
            if isinstance(v, list):
                files = []
                for ex_path in v:
                    all_path = os.sep.join([TEST_FILE_PATH,ex_path])
                    files.append((k, (open(all_path, 'rb'))))
                    # print(all_path)

            else:
                # 单文件上传
                all_path = os.sep.join([TEST_FILE_PATH, v])
                files = {k: open(all_path, 'rb')}
            return files

    @classmethod
    def write_file(cls, file_obj: str, content:str) -> object:
        """file对象处理方法
        :param file_obj: 上传文件使用，格式：接口中文件参数的名称:"文件路径地址"/["文件地址1", "文件地址2"]
        实例- 单个文件: &file&D:
        """
        if file_obj == '' or file_obj is None:
            return
        all_path = os.sep.join([TEST_FILE_PATH, file_obj])
        with open(all_path, "wb") as code:
            code.write(content)
        return all_path


    @classmethod
    def handle_data_fromat(cls, _template, data=None, _no_content=0, _dataType:bool=False):
        if isinstance(_template, str):
            if isinstance(data, list):
                _dict = []
                for _index in range(len(data)):
                    if isinstance(data[_index], dict):
                        _dict.append(cls.handle_data_fromat(_template, data[_index]))
                return _dict
            else:
                return req_expr(content= _template, data= data, _no_content = _no_content, _dataType = _dataType)
        else:
            if isinstance(_template, list):
                for _index in range(len(_template)):
                    _template[_index] = cls.handle_data_fromat(_template[_index], data, _no_content, _dataType)
                return _template
            else:
                if isinstance(_template, dict):
                    for key in _template.keys():
                        if key.find('$') != 0:
                            _template[key] = cls.handle_data_fromat(_template[key], data, _no_content, _dataType)
                return _template



    @classmethod
    def handle_data(cls, variable: str, jsonformat:bool=True) -> dict:
        """请求数据处理
        :param variable: 请求数据，传入的是可转换字典/json的字符串,其中可以包含变量表达式
        return 处理之后的json/dict类型的字典数据
        """
        if variable == '':
            return
        if isinstance(variable, str) and variable.find(".json",len(variable)-5) != -1:
            _path = path.join(TEST_DATA_PATH, variable, )
            with open(_path, "r") as json_file:
                variable = json.load(json_file)
        data = req_expr(variable, cls.response_dict)
        if jsonformat:
            variable = convert_json(data)
        else:
            variable = data
        return variable

    @classmethod
    def handle_sql(cls, sql: str, db: object):
        """处理sql，并将结果写到响应字典中"""
        if sql :
            sql = req_expr(sql, cls.response_dict)
            allure_step('运行sql', sql)
            logger.info(sql)
            # 查后置sql
            result = db.fetch_one(sql)
            allure_step('sql执行结果', {"sql_result": result})
            logger.info(f'结果：{result}')
            if result:
                # 将查询结果添加到响应字典里面，作用在，接口响应的内容某个字段 直接和数据库某个字段比对，在预期结果中
                # 使用同样的语法提取即可
                cls.response_dict.update(result)
        else:
            sql = None
            return

    @classmethod
    def get_key_dic(self, _data, _key):
        _temp = None
        if isinstance(_data,dict):
            _temp = _data.get(_key.strip())
            if _temp is None:
                for c in _data.keys():
                    if str(c).strip().lower() == _key.strip().lower():
                        _temp = _data.get(c)
            if _temp is None:
                for c in _data.keys():
                    _newKey = str(c).strip().lower()
                    if _newKey.find(_key.strip().lower()) != -1 and _newKey.find('_cell'.strip().lower()) < 0:
                        logger.info(f'使用类似数据原始Key:{_key} 新Key:{_newKey}')
                        _temp = _data.get(c)
            return _temp
        if isinstance(_data,list):
            for c in range(len(_data)):
                if str(_data[c]).strip()== _key.strip():
                    _temp = c
            if _temp is None:
                for c in range(len(_data)):
                    if str(_data[c]).strip().lower() == _key.strip().lower():
                        _temp = c
            if _temp is None:
                for c in range(len(_data)):
                    _newKey = _data[c]
                    if str(_newKey).strip().lower().find(_key.strip().lower()) != -1 and _newKey.find('_cell'.strip().lower()) < 0:
                        logger.info(f'使用类似数据原始Key:{_key} 新Key:{_newKey}')
                        _temp = c
            return _temp

    @classmethod
    def check_test_case(datas: list):
        _datas = list()
        try:
            _config = {'key':'atf'}
            _mysql = MysqlDB(_config)
        except Exception as e:
            _mysql = None
        for testdata in datas:
            casename = format_caseName(testdata[Constant.CASE_TITLE])
            if DataProcess.isNotNull(get_system_key(Constant.ISSUE_KEY)) and DataProcess.isNotNull(
                    get_system_key(Constant.TEST_SRTCYCLE_ID)):
                jirakey = get_system_key(Constant.ISSUE_KEY)
                cycleId = get_system_key(Constant.TEST_SRTCYCLE_ID)
                _sql = f"select * from `traffic_test`.`test_autotest_run` where jirakey='{jirakey}' and `status` = '{Constant.STATUS_AUTOTEST}' and cycleId='{cycleId}' and casename='{casename}'"
                _info = _mysql.execute(_sql).fetchall()
                if len(_info) > 0:
                    _datas.append(testdata)
            else:
                if DataProcess.isNotNull(testdata[Constant.CASE_STATUS].strip()) == False or testdata[Constant.CASE_STATUS].strip() != '否':
                    _datas.append(testdata)
                else:
                    if DataProcess.isNotNull(get_system_key(Constant.TEST_CASE_NAME_LIST)):
                        if casename in eval(get_system_key(Constant.TEST_CASE_NAME_LIST)):
                            _datas.append(testdata)
                        else:
                            _datas.append(testdata)
        return _datas


    @classmethod
    def parseJson(self, obj, newObj):
        '''
        递归遍历json
        '''
        for k in obj:
            # 为list的时候
            if isinstance(obj, list):
                if isinstance(k, list):
                    if isinstance(newObj, list):
                        newObj.append(self.parseJson(k, list()))
                    elif isinstance(newObj, dict):
                        newObj[k] = self.parseJson(k, list())
                elif isinstance(k, dict):
                    if isinstance(newObj, list):
                        newObj.append(self.parseJson(k, dict()))
                    elif isinstance(newObj, dict):
                        newObj[k] = self.parseJson(k, dict())
                else:
                    # 这一段 判断key
                    if isinstance(newObj, list):
                        newObj.append(k)
                    elif isinstance(newObj, dict):
                        newObj[k] = k
            # 为dict的时候
            elif isinstance(obj, dict):
                if isinstance(obj[k], list):
                    if isinstance(newObj, list):
                        newObj.append(self.parseJson(obj[k], list()))
                    elif isinstance(newObj, dict):
                        newObj[k] = self.parseJson(obj[k], list())
                elif isinstance(obj[k], dict):
                    if isinstance(newObj, list):
                        newObj.append(self.parseJson(obj[k], dict()))
                    elif isinstance(newObj, dict):
                        newObj[k] = self.parseJson(obj[k], dict())
                else:
                    # 这一段 判断key
                    if isinstance(newObj, list):
                        newObj.append(obj[k])
                    elif isinstance(newObj, dict):
                        newObj[k] = obj[k]
        return newObj

    @classmethod
    def getDate(self,now):
        if isinstance(now,str):
            now=int(now)
        timeArray = time.localtime(now)
        _time = time.strftime("%Y-%m-%d %H:%M:%S", timeArray)
        return _time

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
            if isinstance(data,list):
                if data.__len__()==0:
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
            logger.info('判断数据是否为空异常,数据：'+data)
            return True

    @classmethod
    def getDateDiff(self,_date):
        _date = str(_date).strip()
        if len(_date) > 10:
            ts = int(time.mktime(time.strptime(_date, "%Y-%m-%d %H:%M:%S")))
        else:
            ts = int(time.mktime(time.strptime(_date, "%Y-%m-%d")))
        return ts

    @classmethod
    def check_test_data(self, testdatas:list):
        _testDatas=[]
        try:
            for testdata in testdatas:
                casename = format_caseName(testdata[Constant.CASE_TITLE])
                if DataProcess.isNotNull(get_system_key(Constant.TEST_SRTCYCLE_ID)):
                    caserunid = ServicePlatForm.getCaseByCycle(casename, Constant.STATUS_PRE)[
                        'caserunid']
                    if caserunid != '00000':
                        _testDatas.append(testdata)
                else:
                    if Constant.CASE_STATUS in testdata:
                        if testdata[Constant.CASE_STATUS].strip() != '否':
                            _testDatas.append(testdata)
                    else:
                        _testDatas.append(testdata)
            return _testDatas
        except Exception as e:
            logger.info('检查数据中用例属性错误信息异常信息:'+repr(e))
        return _testDatas

    @classmethod
    def getCaseUrlMeta(self, testname, caseurl):
        caseurl = str(caseurl).replace(get_system_key(Constant.CURRENT_PATH) + os.sep, "").strip()
        try:
            testname = format_caseName(testname)
            gitname = get_system_key(Constant.GIT_PROJECTNAME)
            caseArr = caseurl.split('::')
            scripturl = f'http://172.28.22.90/autotest/{gitname}/-/blob/master/{caseArr[0]}'
            if caseArr.__len__() == 3:
                scriptclass = caseArr[1]
                scriptmethod = caseArr[2]
            else:
                scrtpArr = caseArr[1].split(':')
                if scrtpArr.__len__() == 2:
                    scriptclass = scrtpArr[0]
                    scriptmethod = scrtpArr[1]
                else:
                    scriptclass = scrtpArr[0]
                    scriptmethod = scrtpArr[0]
            scriptname = get_system_key(Constant.CURRENT_PATH) + os.sep + caseArr[0]
            return testname,gitname,scripturl, scriptclass, scriptmethod, scriptname
        except Exception as e:
            logger.info(f'解析用例脚本路径URL：用例名称:{testname} 脚本路径:{caseurl} 异常信息：{e}')
            return testname, "", "", "", "",""

    @classmethod
    def is_contain_chinese(self, check_str):
        """
        判断字符串中是否包含中文
        :param check_str: {str} 需要检测的字符串
        :return: {bool} 包含返回True， 不包含返回False
        """
        for ch in check_str:
            if u'\u4e00' <= ch <= u'\u9fff':
                return True
        return False

    @classmethod
    def setDictEncode(self, dict):
        """
        处理header中的特殊字符串 空格、int、float、中文
        :param dict:
        :return:
        """
        for key, value in dict.items():
            if value == " ":
                dict[key] = ""
            if type(value) == type(1):
                dict[key] = str(value)
                continue
            if type(value) == type(1.2):
                dict[key] = str(value)
                continue
            if self.is_contain_chinese(value):
                dict[key] = value.encode('UTF-8')
        return dict


if __name__ == '__main__':
    print('_11'.find('__'))




