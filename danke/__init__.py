# coding:utf-8


import flask_admin
import redis
import logging

from flask_admin import Admin

from config import config_dict
from flask import Flask, session
from flask_sqlalchemy import SQLAlchemy
from flask_wtf.csrf import CSRFProtect
from flask_session import Session
from logging.handlers import RotatingFileHandler
from flask_babelex import Babel

from danke import constants

from danke.utils.commons import RegexConverter


adm = Admin(name=u'danke')

# 后台汉化
babel = Babel()



# 构建数据库对象
db=SQLAlchemy()
redis_store=None


# 为flask补充csrf防护机制
csrf=CSRFProtect()

# 设置日志的记录等级
logging.basicConfig(level=logging.DEBUG)  # 调试debug级
# 创建日志记录器，指明日志保存的路径、每个日志文件的最大大小、保存的日志文件个数上限
file_log_handler = RotatingFileHandler("logs/log", maxBytes=1024*1024*100, backupCount=10)
# 创建日志记录的格式                 日志等级    输入日志信息的文件名 行数    日志信息
formatter = logging.Formatter('%(levelname)s %(filename)s:%(lineno)d %(message)s')
# 为刚创建的日志记录器设置日志记录格式
file_log_handler.setFormatter(formatter)
# 为全局的日志工具对象（flask app使用的）添加日记录器
logging.getLogger().addHandler(file_log_handler)


def create_app(config_name):
    app = Flask(__name__)
    conf=config_dict[config_name]
    app.config.from_object(conf)
    app.config['UPLOAD_FOLDER'] = conf.UPLOAD_FOLDER

    # 初始化db
    db.init_app(app)

    global redis_store
    redis_store = redis.StrictRedis(host=conf.REDIS_HOST, port=conf.REDIS_PORT,password=conf.REDIS_PASSWD)

    # 初始化
    # csrf.init_app(app)

    Session(app)

    # 向app中添加自定义转换器
    app.url_map.converters['re']=RegexConverter

    import danke.api_1_0
    app.register_blueprint(api_1_0.api,url_prefix="/api/v1_0")

    # 提供静态文件
    import danke.web_html
    app.register_blueprint(web_html.html)

    babel.init_app(app)

    # from danke.api_1_0.admin import MyView
    from danke.api_1_0.admin import CustomView, CustomModelView
    from flask.ext.admin.contrib.fileadmin import FileAdmin
    import os.path as op

    from danke.api_1_0.admin import User_info,Addr_info,GoodsType_info,Goods_info,GoodsSku_info,IndexGoodsBanner_info,GoodsImage_info,PromotionBanner_info,OrderInfo_info
    from danke.api_1_0.admin import GoodsColor_info, GoodsModel_info,Superuser_info,Groupadd_info,DiscountCoupons_info,Classify_info

    # Add views here
    adm.init_app(app)

    adm.add_view(Superuser_info(db.session, name=u'管理员',category=u'用户管理'))
    adm.add_view(User_info(db.session, name=u'用户',category=u'用户管理'))
    adm.add_view(Addr_info(db.session, name=u'地址',category=u'用户管理'))
    adm.add_view(Classify_info(db.session, name=u'商品分类',category=u'商品管理'))
    adm.add_view(GoodsType_info(db.session, name=u'商品类型',category=u'商品管理'))
    adm.add_view(Goods_info(db.session, name=u'商品',category=u'商品管理'))
    adm.add_view(GoodsColor_info(db.session, name=u'颜色',category=u'商品管理'))
    adm.add_view(GoodsModel_info(db.session, name=u'型号',category=u'商品管理'))
    adm.add_view(GoodsImage_info(db.session, name=u'商品图片',category=u'商品管理'))
    adm.add_view(GoodsSku_info(db.session, name=u'商品sku',category=u'商品管理'))
    adm.add_view(IndexGoodsBanner_info(db.session, name=u'轮播商品',category=u'商品管理'))
    adm.add_view(PromotionBanner_info(db.session, name=u'广告商品',category=u'商品管理'))
    adm.add_view(OrderInfo_info(db.session, name=u'订单详情',category=u'订单管理'))
    adm.add_view(Groupadd_info(db.session, name=u'拼团表',category=u'订单管理'))
    adm.add_view(DiscountCoupons_info(db.session, name=u'优惠券',category=u'优惠券'))

    path = op.join(op.dirname(__file__), 'static')
    adm.add_view(FileAdmin(path, '/static/', name=u'静态文件'))
    return app


# 后台汉化
@babel.localeselector
def get_locale():
    return session.get('lang','zh_Hans_CN')



