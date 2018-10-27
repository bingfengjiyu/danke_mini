# coding:utf-8
from flask import url_for
from flask.ext.admin import BaseView, expose
from flask_admin.contrib import sqla
from flask_admin.form import ImageUploadField, BaseForm, upload
from markupsafe import Markup
from werkzeug.utils import secure_filename
from wtforms import form
import os.path as op

from danke.models import GoodsImage, Address, User, GoodsType, Goods, GoodsSku, IndexGoodsBanner, PromotionBanner, \
    OrderInfo, GoodsColor, GoodsModel, Superuser, Groupadd, DiscountCoupons, Classify

from flask.ext.admin import BaseView, expose


class CustomView(BaseView):
    """View function of Flask-Admin for Custom page."""

    @expose('/')
    def index(self):
        return self.render('admin/custom.html')

    @expose('/second_page')
    def second_page(self):
        return self.render('admin/second_page.html')


from flask.ext.admin.contrib.sqla import ModelView


class CustomModelView(ModelView):
    """View function of Flask-Admin for Models page."""
    pass


class Addr_info(ModelView):

    column_labels = {
        'id':u'序号',
        'user' : u'所属用户',
        'receiver':u'收件人',
        'pro_city_county':u'城市',
        'addr':u'地址',
        'phone':u'电话',
        'is_default':u'是否默认',
        'create_time':u'创建时间',
        'update_time':u'更新时间'
    }

    column_list = ('id', 'user','receiver','pro_city_county','addr','phone','is_default','create_time','update_time')

    def __init__(self, session, **kwargs):
        super(Addr_info, self).__init__(Address, session, **kwargs)


class Superuser_info(ModelView):
    column_labels = {
        'id': u'管理员ID',
        'name': u'账号',
        'password': u'密码'
    }

    column_list = ('id', 'name', 'password')

    def __init__(self, session, **kwargs):
        super(Superuser_info, self).__init__(Superuser, session, **kwargs)



class User_info(ModelView):
    column_labels = {
        'user_id': u'用户ID',
        'openid': u'openID',
        'name': u'姓名',
        'mobile': u'手机号',
        'real_name': u'真实姓名',
        'id_card': u'身份证号码',
        'avatar_url': u'用户头像',
        'create_time':u'创建时间',
        'update_time': u'更新时间'
    }

    column_list = ('user_id', 'openid', 'name', 'mobile', 'real_name', 'id_card', 'avatar_url','create_time','update_time')

    def __init__(self, session, **kwargs):
        super(User_info, self).__init__(User, session, **kwargs)


class Classify_info(ModelView):
    column_labels = {
        'id': u'分类id',
        'name': u'类型名'
    }

    column_list = ('id', 'name')

    def __init__(self, session, **kwargs):
        super(Classify_info, self).__init__(Classify, session, **kwargs)


class GoodsType_info(ModelView):
    column_labels = {
        'type_id': u'类型id',
        'name': u'类型名',
        'image': u'图片',
        'create_time': u'创建时间',
        'update_time': u'更新时间'
    }

    column_list = ('type_id', 'name', 'image','create_time','update_time')

    def __init__(self, session, **kwargs):
        super(GoodsType_info, self).__init__(GoodsType, session, **kwargs)



class GoodsSku_info(ModelView):
    column_labels = {
        'sku_id': u'商品skuid',
        'typeid': u'类型id',
        'goodsid': u'商品id',
        'name': u'商品名称',
        'price_unit': u'商品单价',
        'group_price': u'拼团价格',
        'pnum': u'商品拼团人数',
        'starttime': u'商品拼团开始时间',
        'endtime': u'商品拼团结束时间',
        'period': u'商品拼团有效时间',
        'package_price': u'套餐价格',
        'image': u'商品图片',
        'stock': u'商品库存',
        'sales': u'商品销量',
        'create_time': u'创建时间',
        'update_time': u'更新时间'
    }

    column_list = ('sku_id', 'typeid', 'goodsid','name','price_unit','group_price','pnum','starttime','endtime','period','package_price','image','stock','sales','create_time','update_time')

    def __init__(self, session, **kwargs):
        super(GoodsSku_info, self).__init__(GoodsSku, session, **kwargs)



class Goods_info(ModelView):
    column_labels = {
        'id': u'商品id',
        'name': u'商品名',
        'detail': u'详情',
        'create_time': u'创建时间',
        'update_time': u'更新时间'
    }

    column_list = ('id', 'name', 'detail','create_time','update_time')

    def __init__(self, session, **kwargs):
        super(Goods_info, self).__init__(Goods, session, **kwargs)



class IndexGoodsBanner_info(ModelView):
    column_labels = {
        'id': u'商品id',
        'sku': u'商品sku',
        'image': u'商品图片',
        'create_time': u'创建时间',
        'update_time': u'更新时间'

    }

    column_list = ('id', 'sku', 'image','create_time','update_time')

    def __init__(self, session, **kwargs):
        super(IndexGoodsBanner_info, self).__init__(IndexGoodsBanner, session, **kwargs)


class GoodsImage_info(ModelView):
    column_labels = {
        'id': u'商品id',
        'sku': u'商品sku',
        'image': u'商品图片',
        'create_time': u'创建时间',
        'update_time': u'更新时间'
    }

    column_list = ('id', 'sku', 'image','create_time','update_time')

    def __init__(self, session, **kwargs):
        super(GoodsImage_info, self).__init__(GoodsImage, session, **kwargs)


class PromotionBanner_info(ModelView):
    column_labels = {
        'id': u'广告商品id',
        'name': u'广告商品名称',
        'url': u'广告链接',
        'image': u'广告图片',
        'create_time': u'创建时间',
        'update_time': u'更新时间'
    }

    column_list = ('id', 'name', 'url','image','create_time','update_time')

    def __init__(self, session, **kwargs):
        super(PromotionBanner_info, self).__init__(PromotionBanner, session, **kwargs)


class OrderInfo_info(ModelView):
    column_labels = {
        'id': u'订单号',
        'user_id': u'用户id',
        'group_id': u'拼团id',
        'addr_id': u'地址id',
        'coupons_id': u'优惠券id',
        'total_count': u'总数量',
        'total_price': u'总价格',
        'status': u'订单状态',
        'parent': u'是否团长',
        'comment': u'评价',
        'trade_no': u'交易编号',
        'create_time': u'创建时间',
        'update_time': u'更新时间'
    }

    column_list = ('id', 'user_id','group_id', 'addr_id','coupons_id', 'total_count', 'total_price','status','parent','comment','trade_no','create_time','update_time')

    def __init__(self, session, **kwargs):
        super(OrderInfo_info, self).__init__(OrderInfo, session, **kwargs)


class GoodsColor_info(ModelView):
    column_labels = {
        'id': u'id',
        'color': u'商品颜色',
        'sku': u'skuid'
    }

    column_list = ('id', 'color', 'sku')

    def __init__(self, session, **kwargs):
        super(GoodsColor_info, self).__init__(GoodsColor, session, **kwargs)



class GoodsModel_info(ModelView):
    column_labels = {
        'id': u'id',
        'model': u'商品型号',
        'sku': u'skuid'
    }

    column_list = ('id', 'model', 'sku')

    def __init__(self, session, **kwargs):
        super(GoodsModel_info, self).__init__(GoodsModel, session, **kwargs)


# 拼团表
class Groupadd_info(ModelView):
    column_labels = {
        'id': u'拼团表id',
        'sku_id': u'skuid',
        'status': u'拼团状态',
        'ptstime': u'拼团开始时间',
        'ptetime': u'拼团结束时间',
        'group_num': u'拼团人数'
    }

    column_list = ('id', 'sku_id','status','ptstime','ptetime','group_num')

    def __init__(self, session, **kwargs):
        super(Groupadd_info, self).__init__(Groupadd, session, **kwargs)


# 优惠券表
class DiscountCoupons_info(ModelView):
    column_labels = {
        'id': u'优惠券id',
        'user_id': u'用户id',
        'name': u'名称',
        'desc': u'优惠券说明',
        'image': u'优惠券图片',
        'starttime': u'开始时间',
        'endtime': u'结束时间',
    }

    column_list = ('id', 'user_id', 'name', 'desc', 'image', 'starttime','endtime')

    def __init__(self, session, **kwargs):
        super(DiscountCoupons_info, self).__init__(DiscountCoupons, session, **kwargs)


# path = op.join(op.dirname(__file__), 'static')
#
#
# class MyV1(sqla.ModelView):
#     def _list_thumbnail(view, context, model, name):
#         if not model.path:
#             return ''
#
#         return Markup('<img src="%s">' % url_for('static',
#                                                  filename=form.thumbgen_filename(model.path)))
#
#     column_formatters = {
#         'image': _list_thumbnail
#     }
#
#     # Alternative way to contribute field is to override it completely.
#     # In this case, Flask-Admin won't attempt to merge various parameters for the field.
#     form_extra_fields = {
#         'image': form.ImageUploadField('Image',
#                                       base_path=file_path,
#                                       thumbnail_size=(100, 100, True))
#     }
#









import os.path as op

path = op.join(op.dirname(__file__), 'static')


def thumb_name(filename):
    name, _ = op.splitext(filename)
    return secure_filename('%s-thumb.jpg' % name)


class MyForm(BaseForm):
    upload = ImageUploadField('File', thumbgen = path)

import os.path as op

form_extra_fields = {
'pics': upload.ImageUploadField(label='图片', base_path = path),
}