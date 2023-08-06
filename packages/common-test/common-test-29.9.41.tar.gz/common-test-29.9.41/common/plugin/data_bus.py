import os
from common.common.constant import Constant
from common.data.data_process import DataProcess
from common.data.handle_common import get_system_key, set_system_key, print_databus_info
from common.file.ReadFile import get_yaml_config
from common.file.handle_file import get_item
from common.plat.ATF_platform import ATFPlatForm
from common.plat.service_platform import ServicePlatForm
from loguru import logger


class DataBus(object):

    @classmethod
    def get_key(cls,_key):
        """
        获取Databus数据
        获取环境变量，config.yaml,config.ini
        :param _key:
        :return:
        """
        try:
            _value = get_system_key(_key)
            if _value is not None:
                return _value
            else:
                _value = get_yaml_config('common.' + _key, False)
                if _value is not None and _value != 'common.'+_key:
                    return _value
                else:
                    env = get_system_key('env')
                    _value = get_yaml_config(env + '.' + _key, False)
                    if _value is not None and _value != env+'.' + _key :
                        return _value
                    else:
                        _arr = _key.split(".")
                        if len(_arr) > 1:
                            _value = ATFPlatForm.getProjectData(_arr[0], _arr[1])
                            if _value:
                                set_system_key(_key, _value)
                            return _value
            loguru.logger.error("未获取到Key:" + _key)
            return _key
        except Exception as e:
            logger.error("获取Key异常:"+_key)
            return _key

    @classmethod
    def set_key(cls,str_key, str_value, _replace:bool=True, type = 1):
        """
        把值设置到Databus
        :param str_key:
        :param str_value:
        :param type: 1--set到环境变量；2--set项目数据，可以重复利用；3--set项目数据，不可以重复利用
        :return:
        """
        if type == 1:
            set_system_key(str_key,str_value,_replace)
        elif type == 2 or type == 3:
            ATFPlatForm.setProjectData(str_key, str_value, type - 2)

    @classmethod
    def del_key(cls,str_key):
        """
        删除Databus的数据
        :param str_key:
        :return:
        """
        del os.environ[str_key]

    @classmethod
    def save_ini(cls,section):
        """
        把config.ini文件的数据存放到环境变量中
        :param section:
        :return:
        """
        for item in get_item(section):
            if item is not None and get_system_key(item[0]) is None:
                os.environ[item[0].strip().lower()] = item[1].strip()

    @classmethod
    def get_param(cls,_replace:bool=True):
        """
        把config.ini文件的数据存放到环境变量中
        :param section:
        :return:
        """
        if DataProcess.isNotNull(get_system_key("param")):
            param = get_system_key("param")
            param_list = param.split(";")
            logger.info("param:"+param)
            for temp in param_list:
                temp_arr = temp.split("=")
                cls.set_key(temp_arr[0].strip(), temp_arr[1].strip(), _replace)



    @classmethod
    def save_yaml(cls, section,_replace:bool=True):
        """
        把配置文件的数据存放到database
        :param section:
        :return:
        """
        dict_a = get_yaml_config(section)
        if isinstance(dict_a,dict) :
            for x in range(len(dict_a)):
                temp_key = list(dict_a.keys())[x]
                temp_value = dict_a[temp_key]
                cls.set_key(temp_key, temp_value, _replace)

    @classmethod
    def get_data(cls, _template, data = None, _no_content = 0, _dataType=False):
        """
        清洗字符串数据
        :param _template: 数据模版：字符串/字典/列表
        :param data: 针对字符串模版，可以设置字典，列表字典          [{'aa':'bb','cc':'dd'},{'aa':'bb','cc':'11'}]
        :return:
        """
        return DataProcess.handle_data_fromat(_template, data, _no_content,_dataType)


    @classmethod
    def get_env(cls):
        """
        获取当前环境
        :return:
        """
        return get_system_key(Constant.ENV)

    @classmethod
    def get_data_atf(cls):
        """
        获取当前环境ATF配置数据
        :return:
        """
        env = cls.get_env()
        projectAlice = get_system_key(Constant.PROJECT_ALICE)
        _data = ServicePlatForm.getATFData(projectAlice, env)
        for key in _data:
            if DataProcess.isNotNull(get_system_key(Constant.RUN_TYPE)):
                cls.set_key(key, _data[key].strip())
            else:
                cls.set_key(key, _data[key].strip(), False)

    @classmethod
    def save_init_data(cls):
        """
        初始化DataBus数据
        :return:
        """
        cls.save_yaml('common.setting', _replace=False)
        cls.save_yaml('common')
        cls.save_yaml(cls.get_env())
        cls.get_data_atf()
        cls.get_param()
        cls.set_key(Constant.Data_init, Constant.Data_init)


    @classmethod
    def run_info(cls):
        """
        打印信息
        :return:
        """
        print_databus_info(Constant.CURRENT_PATH, "项目目录")
        print_databus_info(Constant.PROJECT_NAME, "项目名称")
        print_databus_info(Constant.PORJECT_ID, "项目编号")
        print_databus_info(Constant.ISSUE_KEY, "测试计划")
        print_databus_info(Constant.TEST_TestPlan_ID, "测试计划ID")
        print_databus_info(Constant.TEST_TestPlan_URL,"测试计划地址")
        print_databus_info(Constant.TEST_SRTCYCLE_ID, "测试周期ID")
        print_databus_info(Constant.TEST_SRTCYCLE_NAME, "测试周期名称")
        print_databus_info(Constant.TEST_SRTCYCLE_URL, "测试周期地址")
        print_databus_info(Constant.Jenkins_RESULT, "执行结果")
        print_databus_info(Constant.TEST_CASE_PATH, "执行用例路径")
        print_databus_info(Constant.GIT_PROJECTNAME, "Git项目名称")
        print_databus_info(Constant.ALLURE_PATH, "Allure路径")
        print_databus_info(Constant.TEST_CASE_MARK, "用例等级")
        print_databus_info(Constant.TEST_TYPE, "测试集类型")
        print_databus_info(Constant.RUN_TYPE, "运行方式")
        print_databus_info(Constant.ENV, "运行环境")
        print_databus_info(Constant.PASS_RATE,"预期通过率")
        print_databus_info(Constant.SEND_URSER_LIST, "通知人列表")










