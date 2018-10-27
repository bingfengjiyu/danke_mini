# coding:utf-8

import redis

from danke import constants


class Config(object):
    # SECRET_KEY = "jfhsjfhjsdhfjkwhuieuiwefhew"
    # mysql数据库配置信息
    SQLALCHEMY_DATABASE_URI = constants.SQLALCHEMY_DATABASE_URI
    SQLALCHEMY_TRACK_MODIFICATIONS = True

    # redis
    REDIS_HOST = "127.0.0.1"
    REDIS_PORT = 6379
    REDIS_PASSWD = constants.REDIS_PASSWD

    SESSION_TYPE = "redis"
    SESSION_USE_SIGNER = True
    SESSION_REDIS = redis.StrictRedis(host=REDIS_HOST, port=REDIS_PORT,password=REDIS_PASSWD)
    PERMANENT_SESSION_LIFETIME = 86400

    UPLOAD_FOLDER = constants.UPLOAD_FOLDER




class DevelopmentConfig(Config):
    DEBUG = True



class ProductionConfig(Config):
    pass


config_dict={
    "develop":DevelopmentConfig,
    "product":ProductionConfig
}


