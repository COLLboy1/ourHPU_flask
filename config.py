import redis

class Config(object):
    """配置信息"""
    SECRET_KEY = "ASDSAASASFSAN12321ASDAD"

    # 数据库
    SQLALCHEMY_DATABASE_URI = "mysql+pymysql://root:123456@127.0.0.1:3306/ourhpu"
    SQLALCHEMY_TRACK_MODIFICATIONS = True

    # redis
    REDIS_HOST = "127.0.0.1"
    REDIS_POST = "6379"

    # flask-session配置
    SESSION_TYPE = "REDIS"
    SESSION_REDIS = redis.StrictRedis(host=REDIS_HOST, port=REDIS_POST)
    SESSION_USE_SIGNED = True # 对session_id进行隐藏
    PERMANENT_SESSION_LIFETIME = 86400 # session数据的有效期，单位秒

class DevelopmentConfig(Config):
    """开发模式的配置信息"""
    DEBUG = True

class ProductionConfig(Config):
    """生产环境配置信息"""
    pass

config_map = {
    "develop": DevelopmentConfig,
    "product": ProductionConfig
}