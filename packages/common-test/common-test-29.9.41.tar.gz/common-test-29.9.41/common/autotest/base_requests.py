from common.common.api_driver import APIDriver
from common.plugin.data_bus import DataBus
from loguru import logger
from common.autotest.handle_allure import allure_step
from common.common.constant import Constant
from common.data.data_process import DataProcess
from common.data.handle_common import extractor, get_system_key, set_system_key
from common.file.ReadFile import ReadFile, get_yaml_ApiSchemal
from common.plat.mysql_platform import MysqlPlatForm


class BaseRequest(APIDriver):

    @classmethod
    def send_request(cls, case: dict, host: str = 'host', datatype: str='json') -> object:
        """处理case数据，转换成可用数据发送请求
        :param case: 读取出来的每一行用例内容，可进行解包
        :param env: 环境名称 默认使用config.yaml server下的 dev 后面的基准地址
        return: 响应结果， 预期结果
        """
        DataBus.save_init_data()
        case_number = DataProcess.get_key_dic(case, Constant.CASE_NO)
        path = DataProcess.get_key_dic(case, "接口地址")
        if DataProcess.get_key_dic(case, Constant.CASE_DATA_PARAM) != None:
            parametric_key = DataProcess.get_key_dic(case, Constant.CASE_DATA_PARAM)
        else:
            parametric_key = DataProcess.get_key_dic(case, "入参关键字")

        if DataProcess.get_key_dic(case, Constant.CASE_DATA_HEADER) != None:
            token = DataProcess.get_key_dic(case, Constant.CASE_DATA_HEADER)
        else:
            token = DataProcess.get_key_dic(case, "token操作")
        if DataProcess.get_key_dic(case, Constant.CASE_DATA_TYPE) != None:
            datatype = DataProcess.get_key_dic(case, Constant.CASE_DATA_TYPE)
        method = DataProcess.get_key_dic(case, Constant.CASE_DATA_METHOD)
        file_obj = DataProcess.get_key_dic(case, "上传文件")
        data = DataProcess.get_key_dic(case, Constant.CASE_DATA)
        sql = DataProcess.get_key_dic(case, "后置sql")
        expect = DataProcess.get_key_dic(case, Constant.CASE_EXPECTED)
        is_save = DataProcess.get_key_dic(case, "保存响应")
        url = DataProcess.handle_path(path)
        if url.find("http") == -1:
            url = str(get_system_key(host)) + str(DataProcess.handle_path(path))
        cls._convert_url(url)
        header = DataProcess.handle_header(token)
        try:
            if datatype == 'json':
                data = DataProcess.handle_data(data)
            else:
                data = DataProcess.handle_data(data, False)
        except Exception as e:
            logger.info(f'测试数据：{data} 转换异常:' + repr(e))
        file = DataProcess.handler_files(file_obj)
        desc = f'测试接口详情:{url}'
        # 发送请求
        res = cls.http_request(url=url, method=method, parametric_key=parametric_key,
                               header=DataProcess.setDictEncode(header), data=data, file=file, desc=desc)
        try:
            if DataProcess.isNotNull(get_system_key(Constant.RUN_TYPE)):
                MysqlPlatForm.insert_api_data(url, method, header, data, res.elapsed.total_seconds(), res.status_code)
        except:
            logger.warning("保存请求数据异常")
        # 响应后操作
        if token == '写':
            DataProcess.have_token['Authorization'] = extractor(res.json(), ReadFile.get_config_value('$.expr.token'))
            allure_step('请求头中添加Token', DataProcess.have_token)
        # 保存用例的实际响应
        if is_save == "yes":
            DataProcess.save_response(case_number, res.json())
        try:
            return res.json(), expect, res
        except:
            return res.text, expect, res

    @classmethod
    def api_exec(self, schemal_key, data=None, header=None, file=None, cookie=None, host: str = 'host', datatype: str='json', step:str='测试接口详情') -> object:
        """处理case数据，转换成可用数据发送请求
        :param case: 读取出来的每一行用例内容，可进行解包
        :param env: 环境名称 默认使用config.yaml server下的 dev 后面的基准地址
        return: 响应结果， 预期结果
        """
        DataBus.save_init_data()
        schemal_data = get_yaml_ApiSchemal(schemal_key)
        url = DataProcess.handle_path(schemal_data['url'])
        if url.find("http") == -1:
            url = get_system_key(host) + DataProcess.handle_path(url)
        self._convert_url(url)
        header = DataProcess.handle_header(header)
        try:
            if datatype == 'json':
                data = DataProcess.handle_data(data)
            else:
                data = DataProcess.handle_data(data, False)
        except Exception as e:
            logger.info(f'测试数据：{data} 转换异常:' + repr(e))
        file_obj = DataProcess.handler_files(file)
        if step == '测试接口详情' and DataProcess.isNotNull(schemal_data['desc']):
            step = '测试接口详情:'+schemal_data['desc']
        res = self.http_request(url=url, method=schemal_data['method'], parametric_key=schemal_data['datatype'],
                               header=DataProcess.setDictEncode(header), data=data, file=file_obj, cookie=cookie, desc=step)
        try:
            if DataProcess.isNotNull(get_system_key(Constant.RUN_TYPE)):
                MysqlPlatForm.insert_api_data(url, schemal_data['method'], header, data, res.elapsed.total_seconds(), res.status_code)
        except:
            logger.warning("保存请求数据异常")
        return res

    @classmethod
    def api_request(self, schemal_key, data=None, header=None, file=None, cookie=None, step: str = '测试接口详情') -> object:
        """处理case数据，转换成可用数据发送请求
        :param case: 读取出来的每一行用例内容，可进行解包
        :param env: 环境名称 默认使用config.yaml server下的 dev 后面的基准地址
        return: 响应结果， 预期结果
        """
        DataBus.save_init_data()
        schemal_data = get_yaml_ApiSchemal(schemal_key)
        url = DataProcess.handle_path(schemal_data['url'])
        file_obj = DataProcess.handler_files(file)
        if step == '测试接口详情' and DataProcess.isNotNull(schemal_data['desc']):
            step = '测试接口详情:' + schemal_data['desc']
        res = self.http_request(url=url, method=schemal_data['method'], parametric_key=schemal_data['datatype'],
                               header=header, data=data, file=file_obj, cookie=cookie,
                               desc=step)
        try:
            if DataProcess.isNotNull(get_system_key(Constant.RUN_TYPE)):
                MysqlPlatForm.insert_api_data(url, schemal_data['method'], header, data, res.elapsed.total_seconds(),
                                              res.status_code)
        except:
            logger.warning("保存请求数据异常")
        return res

    @classmethod
    def request(self, url, method, parametric_key=None, header=None, data=None, file=None, cookie=None,  datatype: str='json',desc: str = '测试接口详情'):
        DataBus.save_init_data()
        try:
            if datatype == 'json':
                data = DataProcess.handle_data(data)
            else:
                data = DataProcess.handle_data(data, False)
        except Exception as e:
            logger.info(f'测试数据：{data} 转换异常:' + repr(e))
        file_obj = DataProcess.handler_files(file)
        res = self.http_request(url=DataProcess.handle_path(url), method=method, parametric_key=parametric_key,
                               header=DataProcess.setDictEncode(DataProcess.handle_header(header)), data=data,
                               file=file_obj, cookie=cookie,desc=desc)
        try:
            if DataProcess.isNotNull(get_system_key(Constant.RUN_TYPE)):
                MysqlPlatForm.insert_api_data(url, method, header, data, res.elapsed.total_seconds(),
                                              res.status_code)
        except:
            logger.warning("保存请求数据异常")
        return res


    @classmethod
    def _convert_url(self,url):
        _url = url.replace("//", '####').split('/')
        _newurl = '';
        for i in range(len(_url)):
            if _url[i].find(Constant.DATA_NO_CONTENT) == -1:
                _newurl = _newurl + _url[i] + '/'
        _newurl = _newurl.replace("//", "/").replace("####", "//")
        return _newurl












