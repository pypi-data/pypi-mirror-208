import pymysql
from loguru import logger
from common.data.handle_common import print_info

class MysqlBatch:

    conn = None

    def __init__(self, config):
        """初始化连接Mysql"""
        self.conn = pymysql.connect(
            host=config.get("host"),
            port=config.get("port"),
            user=config.get("user"),
            password=config.get("password"),
            db=config.get("db_name"),
            charset='utf8mb4',
            cursorclass=pymysql.cursors.DictCursor
        )

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
        self.conn.commit()
        self.conn.close()

    def close(self):
        """关闭数据库连接"""
        self.conn.close()