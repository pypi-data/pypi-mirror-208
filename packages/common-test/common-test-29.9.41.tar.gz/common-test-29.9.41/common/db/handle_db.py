import os

import pymysql
from loguru import logger
from common.data.handle_common import print_info
from common.common.api_driver import APIDriver
from common.common.constant import Constant


class MysqlDB:

    conn = None

    def __init__(self, config):
        """初始化连接Mysql"""
        if config.get("host") is not None:
            self.conn = pymysql.connect(
                host=config.get("host"),
                port=config.get("port"),
                user=config.get("user"),
                password=config.get("password"),
                db= config.get("db_name"),
                charset='utf8mb4',
                cursorclass=pymysql.cursors.DictCursor
            )
        if config.get("key") is not None:
             db_config = self.get_db_config(config.get("key"),config.get("env"))
             self.conn = pymysql.connect(
                 host=db_config.get('host'),
                 port=db_config.get('port'),
                 user=db_config.get("dbUsername"),
                 password=db_config.get("dbPasswd"),
                 db=db_config.get("dbName"),
                 charset='utf8mb4',
                 cursorclass=pymysql.cursors.DictCursor
             )
        if config.get("atf") is not None:
            db_config = self.get_db_config(os.environ['ATFDB'], os.environ['ATFEVN'])
            self.conn = pymysql.connect(
                host=db_config.get('host'),
                port=db_config.get('port'),
                user=db_config.get("dbUsername"),
                password=db_config.get("dbPasswd"),
                db=db_config.get("dbName"),
                charset='utf8mb4',
                cursorclass=pymysql.cursors.DictCursor
            )


    def get_db_config(self, db_key, db_env):
        _tempdata = APIDriver.http_request(url=f"{Constant.ATF_URL_API}/getDBConfig/{db_key}/{db_env}",
                                           method='get'
                                           )
        return _tempdata.json()

    def fetch_one(self, sql: str) -> object:
        """查询数据，查一条"""
        with self.conn.cursor() as cur:
            cur.execute(sql)
            result = cur.fetchone()
            # 使用commit解决查询数据出现概率查错问题
            self.conn.commit()
        return result

    def execute(self, query_string: str):
        """
        只允许执行 SELECT 与 INSERT 语句
        """
        try:
            single_query = query_string.replace(";", "")
            print_info('Mysql准备执行sql语句，%s' % single_query)
            sql_type = single_query.strip().split(" ")[0].lower()  # 从语句中提取第一个字符串判断sql类型。
            if "select" == sql_type or "insert" == sql_type or "delete":
                cursor = self.conn.cursor()
                cursor.execute(single_query)
                print_info("Mysql sql执行成功")
                return cursor
            else:
                logger.error("不支持其他语句类型执行，请检查sql")
        except Exception as e:
            logger.info(f'执行SQL异常:'+query_string)
            return ""

    def executemany(self, query_string: str, _data):
        """
        只允许执行 SELECT 与 INSERT 语句
        """
        single_query = query_string.split(';')[0]
        print_info('Mysql准备执行sql语句，%s' % single_query)
        sql_type = single_query.strip().split(" ")[0].lower()  # 从语句中提取第一个字符串判断sql类型。
        if "select" == sql_type or "insert" == sql_type or "delete":
            cursor = self.conn.cursor()
            cursor.executemany(single_query, _data)
            print_info("Mysql sql执行成功")
            return cursor
        else:
            logger.error("不支持其他语句类型执行，请检查sql")


    def close(self):
        """关闭数据库连接"""
        self.conn.commit()
        self.conn.close()


