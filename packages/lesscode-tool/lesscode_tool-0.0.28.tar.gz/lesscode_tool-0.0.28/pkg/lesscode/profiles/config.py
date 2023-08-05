# -*- coding: utf-8 -*-
from tornado.options import options
from lesscode.db.connection_info import ConnectionInfo

# 运行环境
options.running_env = "local"
# 项目前缀
options.route_prefix = ""
# 服务启动端口
options.port = 8000

# 日志级别
# 10-DEBUG       输出详细的运行情况，主要用于调试。
# 20-INFO        确认一切按预期运行，一般用于输出重要运行情况。
# 30-WARNING     系统运行时出现未知的事情（如：警告内存空间不足），但是软件还可以继续运行，可能以后运行时会出现问题。
# 40-ERROR       系统运行时发生了错误，但是还可以继续运行。
# 50-CRITICAL    一个严重的错误，表明程序本身可能无法继续运行。
options.logging = "DEBUG"
# 日志文件分割方式，时间与文件大小，默认采用时间分割
# time/size
options.log_rotate_mode = "time"
# 日志文件名前缀
options.log_file_prefix = "log"
# 日志文件间隔的时间单位
# S 秒
# M 分
# H 小时、
# D 天、
# W 每星期（interval==0时代表星期一）
# midnight 每天凌晨
options.log_rotate_when = "D"
# 备份文件的个数，如果超过这个个数，就会自动删除
options.log_file_num_backups = 30

# rabbitmq配置
options.rabbitmq_config = {
    "host": "127.0.0.1",
    "port": 5672,
    "username": "guest",
    "password": "guest"
}

# kafka配置
options.kafka_config = {
    "bootstrap_servers": ["120.92.35.156:8985"]
}

# 金山对象存储配置
options.ks3_connect_config = {"host": "ks3-cn-beijing.ksyun.com", "access_key_id": "123456",
                              "access_key_secret": "123456"}

# 任务调度配置                            
options.scheduler_config = {
    "enable": True
}

# 是否打印sql
options.echo_sql = True

# 数据库连接配置
options.conn_info = [
    ConnectionInfo(dialect="postgresql", host="127.0.0.1", port=5432, user="root", password="root",
                   db_name="test", enable=True),
    ConnectionInfo(dialect="mongodb", name="mongodb", host="127.0.0.1", port=27017, user="root",
                   password="root", enable=True),
    ConnectionInfo(dialect="mysql", name="mysql", host="127.0.0.1", port=3306, user="root",
                   password="root", db_name="test", enable=True),
    ConnectionInfo(dialect="sqlalchemy", name="sa", host="127.0.0.1", port=3306, user="root",
                   password="root", db_name="test", params={"db_type":"mysql"}, enable=True),
    ConnectionInfo(dialect="elasticsearch", name="es", host="127.0.0.1", port=9200, user="root",
                   password="root", enable=True),
    ConnectionInfo(dialect="esapi", name="esapi", host="127.0.0.1", port=9200, user="root",
                   password="root", enable=True),
    ConnectionInfo(dialect="neo4j", name="neo4j", host="127.0.0.1", port=7474, user="neo4j",
                   password="neo4j", db_name="neo4j", enable=True),
    ConnectionInfo(dialect="redis", name="redis", host="localhost", port=6379, user=None,
                   password=None, db_name=1, enable=True)
]

