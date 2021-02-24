from config import config_map

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_session import Session
from flask_wtf import CSRFProtect
from logging.handlers import RotatingFileHandler
import redis
import logging

# 创建数据库
db = SQLAlchemy()

# 创建reids 连接对象
redis_store = None

# 设置日志的的登记
logging.basicConfig(level=logging.DEBUG)
# 创建日志记录器，设置日志的保存路径和每个日志的大小和日志的总大小
file_log_handler = RotatingFileHandler("logs/log", maxBytes=1024 * 1024 * 100, backupCount=10)
# 创建日志记录格式，日志等级，输出日志的文件名 行数 日志信息
formatter = logging.Formatter("%(levelname)s %(filename)s: %(lineno)d %(message)s")
# 为日志记录器设置记录格式
file_log_handler.setFormatter(formatter)
# 为全局的日志工具对象（flaks app使用的）加载日志记录器
logging.getLogger().addHandler(file_log_handler)

# 工厂模式
def create_app(config_name):
    """
    创建flask的应用对象
    :param config:  配置模式的名字（“develop”, "product"）
    :return:
    """
    app = Flask(__name__)

    # 根据配置模式的名字获取配置参数的类
    config_class = config_map.get(config_name)
    app.config.from_object(config_class)

    # 使用app初始化db
    db.init_app(app)

    # 创建redis连接对象
    global redis_store
    redis_store = redis.StrictRedis(host=config_class.REDIS_HOST, port=config_class.REDIS_POST)

    # 利用flask-session,将session数据保存到redis中
    Session(app)

    # 未flask补充csrf防护
    CSRFProtect(app)

    # 注册蓝图
    from ourhpu import api_1_0
    app.register_blueprint(api_1_0.api, url_prefix="/api/v1.0")

    return app