# coding:utf-8
import re

from datetime import datetime
import requests
import base64

import time
from flask import json
from flask import session,request,jsonify,current_app
from sqlalchemy import or_, desc

from danke.api_1_0.upload import api_upload
from danke.models import User, Address, Goods, GoodsType, GoodsSku, IndexGoodsBanner, PromotionBanner, GoodsImage, \
    GoodsColor, GoodsModel, Classify, DiscountCoupons, Coupons_user
from . import api
from danke import db,models,constants,redis_store



#添加商品SPU接口
@api.route('/goods_add', methods=['POST','GET'])
def goods_add():
    req_dict = request.values.to_dict()
    if req_dict is None:
        return jsonify(code=202, msg="参数错误")
    name = req_dict.get("name")
    detail = req_dict.get("detail")

    if not all([name,detail]):
        return jsonify(code=203, msg="参数不完整")

    try:
        goods=Goods(name=name,detail=detail)
    except Exception as e:
        return jsonify(code=207, msg="数据异常")

    try:
        db.session.add(goods)
        db.session.commit()
    except Exception as e:
        current_app.logger.error(e)
        db.session.rollback()
    if goods:
        return jsonify(code=200,msg="添加成功")
    else:
        return jsonify(code=201,msg="非法操作")


# 查询商品SPU接口
@api.route('/goods_list', methods=['POST','GET'])
def goods_list():
    req_dict = request.values.to_dict()
    if not req_dict:
        try:
            goods_list=Goods.query.all()
        except Exception as e:
            current_app.logger.error(e)
            return jsonify(code=210, msg="查询商品信息异常")
    else:
        spu_id=req_dict.get("id")
        if not spu_id:
            return jsonify(code=201, msg="非法操作")
        try:
            goods_list=Goods.query.filter(Goods.id==spu_id).all()
        except Exception as e:
            current_app.logger.error(e)
            return jsonify(code=210, msg="查询商品信息异常")

    if goods_list:
        goods_lists=[]
        for goods in goods_list:
            goods_lists.append(goods.to_dict())
        return jsonify(code=200, msg="请求成功", data={"goods_lists": goods_lists})
    else:
        return jsonify(code=201, msg="非法操作", data=[])


# 修改商品SPU接口
@api.route('/goods_set', methods=['POST','GET'])
def goods_set():
    req_dict = request.values.to_dict()
    if req_dict is None:
        return jsonify(code=202, msg="参数错误")
    spu_id = req_dict.get("id")
    name=req_dict.get("name")
    detail=req_dict.get("detail")

    if not all([spu_id,name,detail]):
        return jsonify(code=203, msg="参数不完整")
    try:
        data={
            "id":spu_id,
            "name":name,
            "detail":detail,
        }
        goods = Goods.query.filter(Goods.id==spu_id).update(data)
        try:
            db.session.commit()
        except Exception as e:
            current_app.logger.error(e)
            db.session.rollback()
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(code=217, msg="修改信息异常")

    if goods:
        return jsonify(code=200, msg="修改成功")
    else:
        return jsonify(code=201, msg="非法操作")


# 删除商品SPU接口
@api.route('/goods_del', methods=['DELETE'])
def goods_del():
    req_dict = request.values.to_dict()
    if req_dict is None:
        return jsonify(code=202, msg="参数错误")
    spu_id = req_dict.get("id")
    try:
        goods_sku=GoodsSku.query.filter(GoodsSku.goodsid==spu_id).all()
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(code=210, msg="查询商品信息异常")

    if not goods_sku:
        goods=Goods.query.filter(Goods.id==spu_id).first()
        try:
            db.session.delete(goods)
            db.session.commit()
            return jsonify(code=200, msg="删除成功")
        except Exception as e:
            current_app.logger.error(e)
            db.session.rollback()
            return jsonify(code=201, msg="非法操作")
    return jsonify(code=214, msg="外键约束异常")


#添加商品类型接口
@api.route('/goodsType_add', methods=['POST','GET'])
def goodsType_add():
    name=request.form.get("name")
    image=api_upload()

    if not image:
        return jsonify(code=201, msg="非法操作")

    if not all([name,image]):
        return jsonify(code=203, msg="参数不完整")

    try:
        goodstype = GoodsType(name=name,image=image)
    except Exception as e:
        return jsonify(code=207, msg="数据异常")

    try:
        db.session.add(goodstype)
        db.session.commit()
    except Exception as e:
        current_app.logger.error(e)
        db.session.rollback()
    if goodstype:
        return jsonify(code=200, msg="添加成功")
    else:
        return jsonify(code=201, msg="非法操作")


# 查询商品类型接口
@api.route('/goodsType_list', methods=['POST','GET'])
def goodsType_list():
    req_dict = request.values.to_dict()
    classify_id = req_dict.get("classify_id")
    if not classify_id:
        return jsonify(code=201, msg="非法操作")

    try:
        gtypes = GoodsType.query.filter(GoodsType.classify_id == classify_id).all()
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(code=210, msg="查询商品信息异常")

    if gtypes:
        goodstypelists=[]
        for gtype in gtypes:
            goodstypelists.append(gtype.to_dict())

        return jsonify(code=200, msg="请求成功", data={"goodstypelists":goodstypelists})
    else:
        return jsonify(code=201, msg="请求失败", data={})



# 修改商品类型接口
@api.route('/goodsType_set', methods=['POST','GET'])
def goodsType_set():
    # req_dict = request.values.to_dict()
    # if req_dict is None:
    #     return jsonify(code=202, msg="参数错误")
    # type_id = req_dict.get("type_id")
    # name = req_dict.get("name")
    # image = req_dict.get("image")

    type_id = request.form.get("type_id")
    name = request.form.get("name")
    image = request.form.get("image")

    if not image:
        return jsonify(code=201, msg="非法操作")

    if not all([type_id,name,image]):
        return jsonify(code=203, msg="参数不完整")

    try:
        data = {
            "type_id": type_id,
            "name": name,
            "image": image,
        }
        goodstype = GoodsType.query.filter(GoodsType.type_id == type_id).update(data)
        try:
            db.session.commit()
        except Exception as e:
            current_app.logger.error(e)
            db.session.rollback()
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(code=217, msg="修改信息异常")

    if goodstype:
        return jsonify(code=200, msg="修改成功")
    else:
        return jsonify(code=201, msg="非法操作")


# 删除商品类型接口
@api.route('/goodsType_del', methods=['DELETE'])
def goodsType_del():
    req_dict = request.values.to_dict()
    if req_dict is None:
        return jsonify(code=202, msg="参数错误")
    type_id = req_dict.get("type_id")
    try:
        goods_sku = GoodsSku.query.filter(GoodsSku.typeid == type_id).all()
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(code=210, msg="查询商品信息异常")

    if not goods_sku:
        goodstype = GoodsType.query.filter(GoodsType.type_id == type_id).first()
        try:
            db.session.delete(goodstype)
            db.session.commit()
            return jsonify(code=200, msg="删除成功")
        except Exception as e:
            current_app.logger.error(e)
            db.session.rollback()
            return jsonify(code=201, msg="非法操作")
    return jsonify(code=214, msg="外键约束异常")


#添加商品sku接口
@api.route('/goodsSku_add', methods=['POST','GET'])
def goodsSku_add():
    req_dict = request.values.to_dict()
    if req_dict is None:
        return jsonify(code=202, msg="参数错误")
    typeid = req_dict.get("typeid")
    goodsid = req_dict.get("goodsid")
    name = req_dict.get("name")
    price_unit = req_dict.get("price_unit")
    group_price = req_dict.get("group_price")
    pnum = req_dict.get("pnum")
    starttime = req_dict.get("starttime")
    endtime = req_dict.get("endtime")
    package_price = req_dict.get("package_price")
    image = req_dict.get("image")
    stock = req_dict.get("stock")
    sales = req_dict.get("sales")

    if not all([typeid, goodsid, name,price_unit,group_price,pnum,starttime,endtime,package_price,image,stock,sales]):
        return jsonify(code=203, msg="参数不完整")

    try:
        gtype = GoodsType.query.filter(GoodsType.type_id==typeid).all()
        goods = Goods.query.filter(Goods.id==goodsid).all()
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(code=210, msg="查询信息异常")

    if not all([gtype,goods]):
        return jsonify(code=215, msg="输入的id不存在")

    try:
        gsku = GoodsSku.query.filter_by(name=name, goodsid=goodsid,typeid=typeid).first()
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(code=210, msg="查询信息异常")

    if sales>=stock:
        return jsonify(code=216, msg="销量不能大于库存")

    if gsku is None:
        try:
            goodsSku = GoodsSku(typeid=typeid,goodsid=goodsid,name=name, price_unit=price_unit,group_price=group_price,pnum=pnum,starttime=starttime,endtime=endtime,package_price=package_price,stock=stock,sales=sales,image=image)
        except Exception as e:
            return jsonify(code=207, msg="数据异常")

        try:
            db.session.add(goodsSku)
            db.session.commit()
        except Exception as e:
            current_app.logger.error(e)
            db.session.rollback()
    else:
        return jsonify(code=208,msg="商品已存在")

    if goodsSku:
        return jsonify(code=200, msg="添加成功")
    else:
        return jsonify(code=201, msg="非法操作")


# 查询商品sku接口
@api.route('/goodsSku_list', methods=['POST','GET'])
def goodsSku_list():
    req_dict = request.values.to_dict()
    sku_id = req_dict.get("sku_id")
    if not sku_id:
        return jsonify(code=201, msg="非法操作")
    try:
        goodsSku = GoodsSku.query.filter(GoodsSku.sku_id == sku_id).first()
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(code=210, msg="查询商品信息异常")

    if goodsSku:
        return jsonify(code=200, msg="请求成功", data={"goodsSku": goodsSku.to_dict()})
    else:
        return jsonify(code=201, msg="非法操作", data=[])


# 修改商品sku接口
@api.route('/goodsSku_set', methods=['POST','GET'])
def goodsSku_set():
    req_dict = request.values.to_dict()
    if req_dict is None:
        return jsonify(code=202, msg="参数错误")
    sku_id = req_dict.get("sku_id")
    typeid = req_dict.get("typeid")
    goodsid = req_dict.get("goodsid")
    name = req_dict.get("name")
    price_unit = req_dict.get("price_unit")
    group_price = req_dict.get("group_price")
    pnum = req_dict.get("pnum")
    starttime = req_dict.get("starttime")
    endtime = req_dict.get("endtime")
    package_price = req_dict.get("package_price")
    image = req_dict.get("image")
    stock = req_dict.get("stock")
    sales = req_dict.get("sales")

    if not all([sku_id,typeid, goodsid, name,price_unit,group_price,pnum,starttime,endtime,package_price,image,stock,sales]):
        return jsonify(code=203, msg="参数不完整")

    try:
        gtype = GoodsType.query.filter(GoodsType.type_id==typeid).all()
        goods = Goods.query.filter(Goods.id==goodsid).all()
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(code=210, msg="查询信息异常")

    if not all([gtype,goods]):
        return jsonify(code=215, msg="输入的id不存在")

    if sales>=stock:
        return jsonify(code=216, msg="销量不能大于库存")

    try:
        data = {
            "sku_id": sku_id,
            "typeid": typeid,
            "goodsid": goodsid,
            "name": name,
            "price_unit": price_unit,
            "group_price": group_price,
            "pnum": pnum,
            "starttime": starttime,
            "endtime": endtime,
            "package_price": package_price,
            "image": image,
            "stock": stock,
            "sales": sales,
        }
        goodsSku = GoodsSku.query.filter(GoodsSku.sku_id == sku_id).update(data)
        try:
            db.session.commit()
        except Exception as e:
            current_app.logger.error(e)
            db.session.rollback()
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(code=217, msg="修改信息异常")

    if goodsSku:
        return jsonify(code=200, msg="修改成功")
    else:
        return jsonify(code=201, msg="非法操作")


# 删除商品sku接口
@api.route('/goodsSku_del', methods=['DELETE'])
def goodsSku_del():
    req_dict = request.values.to_dict()
    if req_dict is None:
        return jsonify(code=202, msg="参数错误")
    sku_id = req_dict.get("sku_id")

    try:
        goods_sku = GoodsSku.query.filter(GoodsSku.sku_id == sku_id).first()
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(code=210, msg="查询信息异常")

    if goods_sku:
        try:
            db.session.delete(goods_sku)
            db.session.commit()
            return jsonify(code=200, msg="删除成功")
        except Exception as e:
            current_app.logger.error(e)
            db.session.rollback()
            return jsonify(code=201, msg="非法操作")
    else:
        return jsonify(code=215, msg="输入的id不存在")


# 添加轮播商品接口
@api.route('/indexGoodsbanner_add', methods=['POST','GET'])
def indexGoodsbanner_add():
    req_dict = request.values.to_dict()
    if req_dict is None:
        return jsonify(code=202, msg="参数错误")
    sku_id = req_dict.get("sku")
    image = req_dict.get("image")

    if not all([sku_id, image]):
        return jsonify(code=203, msg="参数不完整")

    try:
        goodsBanner=IndexGoodsBanner.query.filter(IndexGoodsBanner.image == image).all()
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(code=210, msg="查询信息异常")
    if goodsBanner:
        return jsonify(code=208, msg="商品已存在")

    try:
        goods_sku = GoodsSku.query.filter(GoodsSku.sku_id == sku_id).first()
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(code=210, msg="查询信息异常")

    if not goods_sku:
        return jsonify(code=215, msg="输入的id不存在")
    try:
        indexGoodsbanner=IndexGoodsBanner(sku=sku_id,image=image)
    except Exception as e:
        return jsonify(code=207, msg="数据异常")
    try:
        db.session.add(indexGoodsbanner)
        db.session.commit()
    except Exception as e:
        current_app.logger.error(e)
        db.session.rollback()

    if indexGoodsbanner:
        return jsonify(code=200, msg="添加成功")
    else:
        return jsonify(code=201, msg="非法操作")


# 查询轮播商品接口
@api.route('/indexGoodsbanner_list', methods=['POST','GET'])
def indexGoodsbanner_list():
    req_dict = request.values.to_dict()
    if not req_dict:
        try:
            indexGoodsbanner = IndexGoodsBanner.query.all()
        except Exception as e:
            current_app.logger.error(e)
            return jsonify(code=210, msg="查询商品信息异常")
    else:
        id = req_dict.get("id")
        if not id:
            return jsonify(code=201, msg="非法操作")
        try:
            indexGoodsbanner = IndexGoodsBanner.query.filter(IndexGoodsBanner.id == id).all()
        except Exception as e:
            current_app.logger.error(e)
            return jsonify(code=210, msg="查询商品信息异常")

    if indexGoodsbanner:
        indexGoodsbannerlists = []
        for goodsbanner in indexGoodsbanner:
            indexGoodsbannerlists.append(goodsbanner.to_dict())
        return jsonify(code=200, msg="请求成功", data={"indexGoodsbannerlists": indexGoodsbannerlists})
    else:
        return jsonify(code=201, msg="非法操作", data=[])


# 修改轮播商品接口
@api.route('/indexGoodsbanner_set', methods=['POST','GET'])
def indexGoodsbanner_set():
    req_dict = request.values.to_dict()
    if req_dict is None:
        return jsonify(code=202, msg="参数错误")
    id = req_dict.get("id")
    sku = req_dict.get("sku")
    image = req_dict.get("image")

    if not all([id,sku,image]):
        return jsonify(code=203, msg="参数不完整")

    try:
        indexGoodsbanner = IndexGoodsBanner.query.filter(IndexGoodsBanner.id == id).first()
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(code=210, msg="查询商品信息异常")

    if not indexGoodsbanner:
        return jsonify(code=215, msg="输入的id不存在")

    try:
        data = {
            "sku": sku,
            "image": image,
        }
        indexGoodsBanner = IndexGoodsBanner.query.filter(IndexGoodsBanner.id == id).update(data)
        try:
            db.session.commit()
        except Exception as e:
            current_app.logger.error(e)
            db.session.rollback()
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(code=217, msg="修改信息异常")

    if indexGoodsBanner:
        return jsonify(code=200, msg="修改成功")
    else:
        return jsonify(code=201, msg="非法操作")


# 删除轮播商品接口
@api.route('/indexGoodsbanner_del', methods=['DELETE'])
def indexGoodsbanner_del():
    req_dict = request.values.to_dict()
    if req_dict is None:
        return jsonify(code=202, msg="参数错误")
    id = req_dict.get("id")

    try:
        indexGoodsBanner = IndexGoodsBanner.query.filter(IndexGoodsBanner.id == id).first()
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(code=210, msg="查询信息异常")

    if indexGoodsBanner:
        try:
            db.session.delete(indexGoodsBanner)
            db.session.commit()
            return jsonify(code=200, msg="删除成功")
        except Exception as e:
            current_app.logger.error(e)
            db.session.rollback()
            return jsonify(code=201, msg="非法操作")
    else:
        return jsonify(code=215, msg="输入的id不存在")


# 添加广告接口
@api.route('/promotionBanner_add', methods=['POST','GET'])
def promotionBanner_add():
    req_dict = request.values.to_dict()
    if req_dict is None:
        return jsonify(code=202, msg="参数错误")
    sku_id = req_dict.get("sku_id")
    image = req_dict.get("image")

    if not all([sku_id, image]):
        return jsonify(code=203, msg="参数不完整")

    try:
        promotionbanner=PromotionBanner.query.all()
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(code=210, msg="查询信息异常")
    if promotionbanner:
        return jsonify(code=208, msg="商品已存在,只能增加一个")

    try:
        promotion_banner=PromotionBanner(sku=sku_id,image=image)
    except Exception as e:
        return jsonify(code=207, msg="数据异常")
    try:
        db.session.add(promotion_banner)
        db.session.commit()
    except Exception as e:
        current_app.logger.error(e)
        db.session.rollback()

    if promotion_banner:
        return jsonify(code=200, msg="添加成功")
    else:
        return jsonify(code=201, msg="非法操作")


# 查询广告接口
@api.route('/promotionBanner_list', methods=['POST','GET'])
def promotionBanner_list():
    try:
        promotionbanner = PromotionBanner.query.first()
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(code=210, msg="查询商品信息异常")

    if promotionbanner:
        return jsonify(code=200, msg="请求成功", data=promotionbanner.to_dict())
    else:
        return jsonify(code=201, msg="非法操作", data=[])


# 修改广告接口
@api.route('/promotionBanner_set', methods=['POST','GET'])
def promotionBanner_set():
    req_dict = request.values.to_dict()
    if req_dict is None:
        return jsonify(code=202, msg="参数错误")
    id = req_dict.get("id")
    sku_id = req_dict.get("sku_id")
    image = req_dict.get("image")

    if not all([id,sku_id,image]):
        return jsonify(code=203, msg="参数不完整")

    try:
        promotionbanner = PromotionBanner.query.filter(PromotionBanner.id == id).first()
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(code=210, msg="查询商品信息异常")

    if not promotionbanner:
        return jsonify(code=215, msg="输入的id不存在")

    try:
        data = {
            "sku_id": sku_id,
            "image": image,
        }
        promotion_banner = PromotionBanner.query.filter(PromotionBanner.id == id).update(data)
        try:
            db.session.commit()
        except Exception as e:
            current_app.logger.error(e)
            db.session.rollback()
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(code=217, msg="修改信息异常")

    if promotion_banner:
        return jsonify(code=200, msg="修改成功")
    else:
        return jsonify(code=201, msg="非法操作")


# 删除广告接口
@api.route('/promotionBanner_del', methods=['DELETE'])
def promotionBanner_del():
    req_dict = request.values.to_dict()
    if req_dict is None:
        return jsonify(code=202, msg="参数错误")

    id = req_dict.get("id")

    try:
        promotionbanner = PromotionBanner.query.filter(PromotionBanner.id == id).first()
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(code=210, msg="查询信息异常")

    if promotionbanner:
        try:
            db.session.delete(promotionbanner)
            db.session.commit()
            return jsonify(code=200, msg="删除成功")
        except Exception as e:
            current_app.logger.error(e)
            db.session.rollback()
            return jsonify(code=201, msg="非法操作")
    else:
        return jsonify(code=215, msg="输入的id不存在")


# 添加商品图片接口
@api.route('/goodsimage_add', methods=['POST','GET'])
def goodsimage_add():
    req_dict = request.values.to_dict()
    if req_dict is None:
        return jsonify(code=202, msg="参数错误")
    sku_id = req_dict.get("sku")
    image = req_dict.get("image")

    if not all([sku_id,image]):
        return jsonify(code=203, msg="参数不完整")

    try:
        goods_sku=GoodsSku.query.filter(GoodsSku.sku_id==sku_id).first()
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(code=210, msg="查询商品信息异常")

    if not goods_sku:
        return jsonify(code=201, msg="非法操作")

    try:
        goodsimage=GoodsImage(sku=sku_id,image=image)
    except Exception as e:
        return jsonify(code=207, msg="数据异常")

    try:
        db.session.add(goodsimage)
        db.session.commit()
    except Exception as e:
        current_app.logger.error(e)
        db.session.rollback()
    if goodsimage:
        return jsonify(code=200,msg="添加成功")
    else:
        return jsonify(code=201,msg="非法操作")


# 查询商品图片接口
@api.route('/goodsimage_list', methods=['POST','GET'])
def goodsimage_list():
    req_dict = request.values.to_dict()
    if not req_dict:
        try:
            goodsimage_list=GoodsImage.query.all()
        except Exception as e:
            current_app.logger.error(e)
            return jsonify(code=210, msg="查询商品信息异常")
    else:
        sku_id=req_dict.get("sku")
        if not sku_id:
            return jsonify(code=201, msg="非法操作")

        try:
            goods_sku = GoodsSku.query.filter(GoodsSku.sku_id == sku_id).all()
        except Exception as e:
            current_app.logger.error(e)
            return jsonify(code=210, msg="查询商品信息异常")

        if not goods_sku:
            return jsonify(code=201, msg="非法操作")

        try:
            goodsimage_list=GoodsImage.query.filter(GoodsImage.sku==sku_id).all()
        except Exception as e:
            current_app.logger.error(e)
            return jsonify(code=210, msg="查询商品信息异常")

    if goodsimage_list:
        goodsimage_lists=[]
        for goodsimage in goodsimage_list:
            goodsimage_lists.append(goodsimage.to_dict())
        return jsonify(code=200, msg="请求成功", data={"goodsimage_lists": goodsimage_lists})
    else:
        return jsonify(code=201, msg="非法操作", data=[])


# 修改商品图片接口
@api.route('/goodsimage_set', methods=['POST','GET'])
def goodsimage_set():
    req_dict = request.values.to_dict()
    if req_dict is None:
        return jsonify(code=202, msg="参数错误")
    id = req_dict.get("id")
    sku_id=req_dict.get("sku")
    image=req_dict.get("image")

    if not all([id,sku_id,image]):
        return jsonify(code=203, msg="参数不完整")

    try:
        goods_sku = GoodsSku.query.filter(GoodsSku.sku_id == sku_id).first()
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(code=210, msg="查询商品信息异常")

    if not goods_sku:
        return jsonify(code=201, msg="非法操作")

    try:
        data={
            "id":id,
            "sku":sku_id,
            "image":image,
        }
        goodsimage = GoodsImage.query.filter(GoodsImage.id==id).update(data)
        try:
            db.session.commit()
        except Exception as e:
            current_app.logger.error(e)
            db.session.rollback()
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(code=217, msg="修改信息异常")

    if goodsimage:
        return jsonify(code=200, msg="修改成功")
    else:
        return jsonify(code=201, msg="非法操作")


# 删除商品图片接口
@api.route('/goodsimage_del', methods=['DELETE'])
def goodsimage_del():
    req_dict = request.values.to_dict()
    if req_dict is None:
        return jsonify(code=202, msg="参数错误")
    id = req_dict.get("id")
    try:
        goodsimage=GoodsImage.query.filter(GoodsImage.id==id).first()
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(code=210, msg="查询商品信息异常")

    if goodsimage:
        try:
            db.session.delete(goodsimage)
            db.session.commit()
            return jsonify(code=200, msg="删除成功")
        except Exception as e:
            current_app.logger.error(e)
            db.session.rollback()
            return jsonify(code=201, msg="非法操作")
    return jsonify(code=214, msg="外键约束异常")


# 查询商品型号颜色接口
@api.route('/goodsmodel_list', methods=['POST','GET'])
def goodsmodel_list():
    req_dict = request.values.to_dict()
    goods_id = req_dict.get("goods_id")
    if not goods_id:
        return jsonify(code=201, msg="非法操作")
    try:
        goods = Goods.query.filter(Goods.id == goods_id).first()
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(code=210, msg="查询商品信息异常")

    if goods:
        return jsonify(code=200, msg="请求成功",data=goods.get_model())
    else:
        return jsonify(code=201, msg="请求失败",data={})


# 搜素查询接口
@api.route('/classify_list', methods=['POST','GET'])
def classify_list():
    try:
        classifys=Classify.query.all()
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(code=210, msg="查询商品信息异常")

    if classifys:
        classifylist=[]
        for classify in classifys:
            classifylist.append(classify.to_dict())
        return jsonify(code=200, msg="请求成功",data={"classifylist":classifylist})
    else:
        return jsonify(code=201, msg="请求失败",data={})


# 自选套餐接口
@api.route('/typegoods_list', methods=['POST','GET'])
def typegoods_list():
    try:
        goodstypes=GoodsType.query.all()
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(code=210, msg="查询商品信息异常")

    if goodstypes:
        goodsType_list=[]
        for goodstype in goodstypes:
            goodsType_list.append(goodstype.to_skudict())
        return jsonify(code=200, msg="请求成功",data={"goodsType_list":goodsType_list})
    else:
        return jsonify(code=201, msg="请求失败",data={})


# 套餐组合价格接口
@api.route('/typegoods_add', methods=['POST','GET'])
def typegoods_add():
    req_dict = request.values.to_dict()
    sku_list = req_dict.get("sku_list")
    num = req_dict.get("num")
    total_price=0

    for sku_id in sku_list.split(","):
        try:
            sku = GoodsSku.query.filter(GoodsSku.sku_id == sku_id).first()
            total_price+=int(sku.package_price*100)
            total = int(total_price) * int(num) / 100
        except Exception as e:
            current_app.logger.error(e)
            return jsonify(code=210, msg="查询商品信息异常")
    if sku:
        return jsonify(code=200, msg="请求成功",data={"total_price":total})
    else:
        return jsonify(code=201, msg="请求失败")


# 筛选接口
@api.route('/filter', methods=['POST','GET'])
def filter():
    req_dict = request.values.to_dict()
    classify_id = req_dict.get("classify_id")
    try:
        classify=Classify.query.filter(Classify.id == classify_id).first()
        print("classify:%s" % classify)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(code=210, msg="查询商品信息异常")

    if classify:
        modellist=[]
        print("classify.model:%s" % classify.model)
        for model in classify.model:
            print("model.id:%s" % model.id)
            mod=GoodsModel.query.filter(GoodsModel.id == model.id).first()
            modellist.append(mod.to_dict())

        return jsonify(code=200, msg="请求成功",data={"classifyname":classify.name,"modellist":modellist})
    else:
        return jsonify(code=201, msg="请求失败",data={})


# 商品分类查询接口
@api.route('/goods_filter', methods=['POST','GET'])
def goods_filter():
    req_dict = request.values.to_dict()
    classify_id = req_dict.get("classify_id")
    type_id = req_dict.get("type_id")
    keyword = req_dict.get("keyword")
    page = req_dict.get("page")
    try:
        page = int(page)
    except Exception:
        page = 1

    try:
        classify=Classify.query.filter(Classify.id == classify_id).first()
        print("classify:%s" % classify)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(code=210, msg="查询商品信息异常")

    for type in classify.type:
        print("type.type_id:%s" % type.type_id)
        if type.type_id==int(type_id):
            print("-------")
            print("type.type_id:%s" % type.type_id)
            try:
                if keyword=="sort":
                    skuobj = GoodsSku.query.filter(GoodsSku.typeid == type_id).order_by(desc("sales"),desc("create_time"),desc("price_unit"))
                if keyword=="sales":
                    skuobj = GoodsSku.query.filter(GoodsSku.typeid == type_id).order_by(desc("sales"))
                if keyword=="new":
                    skuobj = GoodsSku.query.filter(GoodsSku.typeid == type_id).order_by(desc("create_time"))
                if keyword=="price_desc":
                    skuobj = GoodsSku.query.filter(GoodsSku.typeid == type_id).order_by(desc("price_unit"))
                if keyword=="price_asc":
                    print("-------")
                    skuobj = GoodsSku.query.filter(GoodsSku.typeid == type_id).order_by("price_unit")
                    print("skuobj1:%s" % skuobj)
            except Exception as e:
                    current_app.logger.error(e)
                    return jsonify(code=210, msg="查询商品信息异常")

    try:
        print("skuobj2:%s" % skuobj)
        sku_page = skuobj.paginate(page, constants.GOODS_LIST_PAGE, False)
        print("sku_page:%s" % sku_page)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(code=210, msg="查询商品信息异常")
    sku_list=sku_page.items
    total_page=sku_page.pages
    if sku_list:
        goods_lists=[]
        for goodssku in sku_list:
            gimage=GoodsImage.query.filter(GoodsImage.sku == goodssku.sku_id).first()
            goodsSku_dict=goodssku.to_skudict()
            goodsSku_dict["image"]="https://ceshi.datebook.cc:80/static"+gimage.image
            goods_lists.append(goodsSku_dict)
        print(goods_lists)
        return jsonify(code=200, msg="请求成功",data={"goods_lists":goods_lists,"total_page":total_page,"current_page":page})
    else:
        return jsonify(code=201, msg="请求失败",data={})


# 准备买接口
@api.route('/filter', methods=['POST','GET'])
def ready_buy():
    req_dict = request.values.to_dict()
    user_id = req_dict.get("user_id")
    color_id = req_dict.get("color_id")
    model_id = req_dict.get("model_id")
    sku_id = req_dict.get("sku_id")
    type = req_dict.get("type")
    num = req_dict.get("num")

    if not all([user_id,color_id,model_id,sku_id,type,num]):
        return jsonify(code=203, msg="参数不完整")

    try:
        ad = Address.query.filter_by(user=user_id, is_default=1).first()

        # 查出对应sku_id的商品
        goods=GoodsSku.query.filter(GoodsSku.sku_id == sku_id).first()
        # 通过该商品的goods_id,color_id,model_id找到选中的商品
        good=GoodsSku.query.filter(GoodsSku.goodsid == goods.goodsid,GoodsSku.color_id==color_id,GoodsSku.model_id==model_id).first()

        color = GoodsColor.query.filter(GoodsColor.id == color_id).first()
        model = GoodsModel.query.filter(GoodsModel.id == model_id).first()
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(code=210, msg="查询地址信息异常")

    if good:
        if type=="1":
            price = good.price_unit
            total_price = goods.price_unit * int(num)
        elif type=="2":
            price = good.group_price

    coupons_list = []
    for coupons in goods.coupons:
        print(coupons.id)
        try:
            # 领取优惠券的对象
            couponsuser = Coupons_user.query.filter(Coupons_user.user_id == user_id,
                                                    Coupons_user.coupons_id == coupons.id).first()
        except Exception as e:
            current_app.logger.error(e)
            return jsonify(code=210, msg="查询信息异常")

        if couponsuser.status == "0":
            try:
                # 优惠券的对象
                coupons = DiscountCoupons.query.filter(DiscountCoupons.id == coupons.id).first()
            except Exception as e:
                current_app.logger.error(e)
                return jsonify(code=209, msg="数据为空")

            start_seconds = int(time.mktime(coupons.starttime.timetuple()))
            print(start_seconds)
            end_seconds = int(time.mktime(coupons.endtime.timetuple()))
            print(end_seconds)
            nowtime = int(time.mktime(datetime.now().timetuple()))

            # 可用的优惠券
            if (total_price > coupons.spendMoney) and (nowtime < end_seconds) and (nowtime > start_seconds):
                print("coupons.to_dict():%s" % coupons.to_dict())
                coupons_list.append(coupons.to_dict())

    goodsinfo={
        "name":good.name,
        "sku_img":good.sku_img,
        "color":color.color,
        "model":model.model,
        "price":price,
        "num":num
    }

    data = {
        "address":ad.to_dict(),
        "goodsinfo":goodsinfo,
        "coupons_list":coupons_list,
    }
    if all([ad,goods,good,color,model]):
        return jsonify(code=200, msg="请求成功", data=data)
    else:
        return jsonify(code=209, msg="数据为空", data={})


