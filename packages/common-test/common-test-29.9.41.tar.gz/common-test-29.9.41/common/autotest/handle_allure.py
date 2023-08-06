import allure
import json
from loguru import logger
from common.common.constant import Constant
from common.data.handle_common import print_info, get_system_key


def allure_title(title: str) -> None:
    """allure中显示的用例标题"""
    allure.dynamic.title(title)


def allure_feature(feature: str) -> None:
    """allure中显示的用例模块"""
    allure.dynamic.feature(feature)

def allure_testcase_link(_case_link,caseName) -> None:
    allure.dynamic.testcase(_case_link, f'{caseName}')

def allure_story(storyName: str) -> None:
    """allure中显示的用例的需求和需求连接"""
    allure.dynamic.story(storyName)
    # allure_link(storyLink, f'需求详情：{storyName}')

def allure_link(_link: str, _name=None) -> None:
    """allure中显示的用例模块"""
    allure.dynamic.link(url=_link, name=_name)


def allure_suite(_name: str) -> None:
    """allure中显示的用例模块"""
    # _list=_name.strip("/")
    allure.dynamic.suite(_name)
    # allure.dynamic.parent_suite(_list[0])
    # if len(_list) == 2:
    #     allure.dynamic.suite(_list[1])
    # if len(_list) >2:
    #     allure.dynamic.sub_suite(_list[2])


def allure_tag(_name: str) -> None:
    """allure中显示的用例模块"""
    allure.dynamic.tag(_name)

def allure_severity(severity_level: str) -> None:
    """allure中显示的用例等级"""
    if severity_level.strip() == 'P0':
        allure_tag('冒烟测试,回归测试')
    if severity_level.strip() == 'P1':
        allure_tag('回归测试')
    if severity_level.strip() == 'P2':
        allure_tag('回归测试')
    allure.dynamic.severity(convert_severity(severity_level))


def allure_step(step: str, content: str) -> None:
    """
    :param step: 步骤及附件名称
    :param content: 附件内容
    """
    logger.info(f'{step}:{content}')
    try:
        with allure.step(step):
            allure.attach(json.dumps(content, ensure_ascii=False, indent=4), step, allure.attachment_type.TEXT)
    except Exception as e:
        logger.warning(f'{step}：{content} 异常信息'+repr(e))

def allure_api_step(step, request_url, request_type, request_header, request_data, file, res):
    if isNotNull(file):
        file = f'上传文件:{file}\n'
        file_data_html = f'<div>上传文件:<div><textarea rows="2" cols="150" style="BORDER-BOTTOM: 0px solid; BORDER-LEFT: 0px solid; BORDER-RIGHT: 0px solid; BORDER-TOP: 0px solid;">{file}</textarea></div></div>'
    else:
        file = ""
        file_data_html = ""
    if isNotNull(request_data):
        request_data = f'请求数据:{request_data}\n'
        request_data_html = f'<div>请求数据:<div><textarea rows="2" cols="150" style="BORDER-BOTTOM: 0px solid; BORDER-LEFT: 0px solid; BORDER-RIGHT: 0px solid; BORDER-TOP: 0px solid;">{request_data}</textarea></div></div>'
    else:
        request_data = ""
        request_data_html = ""
    content = f'请求地址:{request_url}\n请求类型：{request_type}\n请求头：{request_header}\n{file}{request_data}'
    try:
        response_status = res.status_code
        response_time = res.elapsed.total_seconds()
        response_data = res.text
        if isNotNull(step):
            logger.info(
                f'步骤描述:{step}\n请求地址:{request_url}\n请求类型：{request_type}\n请求头：{request_header}\n{file}{request_data}响应状态:{response_status}\n响应耗时：{response_time}S\n响应数据：{response_data}')
            template = f'<html><body>' \
                   f'<div>请求地址:<div><textarea rows="1" cols="150" style="BORDER-BOTTOM: 0px solid; BORDER-LEFT: 0px solid; BORDER-RIGHT: 0px solid; BORDER-TOP: 0px solid;">{request_url}</textarea></div></div>' \
                   f'<div>请求类型:<div><textarea rows="1" cols="150" style="BORDER-BOTTOM: 0px solid; BORDER-LEFT: 0px solid; BORDER-RIGHT: 0px solid; BORDER-TOP: 0px solid;">{request_type}</textarea></div></div>' \
                   f'<div>请求头:<div><textarea rows="1" cols="150" style="BORDER-BOTTOM: 0px solid; BORDER-LEFT: 0px solid; BORDER-RIGHT: 0px solid; BORDER-TOP: 0px solid;">{request_header}</textarea></div></div>' \
                   f'{file_data_html}{request_data_html}' \
                   f'<div>响应状态:<div><textarea rows="1" cols="150" style="BORDER-BOTTOM: 0px solid; BORDER-LEFT: 0px solid; BORDER-RIGHT: 0px solid; BORDER-TOP: 0px solid;">{response_status}</textarea></div></div>' \
                   f'<div>响应耗时:<div><textarea rows="3" cols="150" style="BORDER-BOTTOM: 0px solid; BORDER-LEFT: 0px solid; BORDER-RIGHT: 0px solid; BORDER-TOP: 0px solid;">{response_time}S</textarea></div></div>' \
                   f'<div>响应数据:<div><textarea rows="3" cols="150" style="BORDER-BOTTOM: 0px solid; BORDER-LEFT: 0px solid; BORDER-RIGHT: 0px solid; BORDER-TOP: 0px solid;">{response_data}</textarea></div></div>' \
                   f'</body></html>'
            with allure.step(step):
                allure.attach(template, step, allure.attachment_type.HTML)
            if isNotNull(get_system_key(Constant.RESPONSE_CODE)):
                ex_status_code = get_system_key(Constant.RESPONSE_CODE)
                if res.status_code > int(ex_status_code):
                    assert_equals(f'预期状态码:小于{ex_status_code}', f'实际状态码:{res.status_code}', '状态码检查')
        else:
            print_info(
                f'请求地址:{request_url}\n请求类型：{request_type}\n请求头：{request_header}\n 上传文件:{file}\n 请求数据:{request_data}\n 响应状态:{response_status}\n响应耗时：{response_time}S\n响应数据：{response_data}')
    except Exception as e:
        logger.warning(f'{step}：{content} 异常信息' + repr(e))

def convert_severity(_str):
    return _str.replace("P0", "critical").replace("P1", "normal") \
        .replace("P2", "minor").replace("P3", "trivial")


def isNotNull(data):
    try:
        if isinstance(data, bool):
            return data
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
        logger.info('判断数据是否为空异常,数据：'+data)
        return True





if __name__ == '__main__':
    print(int("400"))

