# coding:utf-8
import re

import requests
import base64

from flask import json
from flask import session,request,jsonify,current_app
from danke.models import User,Address, Goods, GoodsType, GoodsSku
from . import api
from danke import db,models,constants,redis_store


# 添加地址
@api.route('/address_add', methods=['POST','GET'])
def address_add():
    req_dict = request.values.to_dict()
    if req_dict is None:
        return jsonify(code=201,msg="参数错误")
    user_id=req_dict.get("user_id")
    print("user_id:%s" % user_id)
    receiver=req_dict.get("receiver")
    phone=req_dict.get("phone")
    pro_city_county=req_dict.get("pro_city_county")
    addr=req_dict.get("addr")
    # is_default=req_dict.get("is_default")

    if not all([user_id,receiver,phone,pro_city_county,addr]):
        return jsonify(code=202,msg="参数不完整")

    if not re.match(r"1[34578]\d{9}", phone):
        return jsonify(code=203, msg="手机号格式不正确")

    try:
        # 查询是否有地址
        check_addr = Address.query.filter(Address.user==user_id).first()
        print("check_addr:%s" % check_addr)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(code=204, msg="查询用户信息异常")

    # 设置是否默认
    if check_addr:
        is_default="1"
        count = Address.query.filter_by(user=user_id).count()
        if count>=10:
            jsonify(code=205,msg="最多添加10条收货地址")
    else:
        is_default="0"

    try:
        # 添加地址
        address = Address(
            user=user_id,
            receiver=receiver,
            phone=phone,
            pro_city_county=pro_city_county,
            addr=addr,
            is_default=is_default
        )
    except Exception as e:
        return jsonify(code=206, msg="数据异常")
    try:
        db.session.add(address)
        db.session.commit()
    except Exception as e:
        current_app.logger.error(e)
        db.session.rollback()
    if address:
        return jsonify(code=200,msg="添加成功")
    else:
        return jsonify(code=207,msg="非法操作")


# 地址列表接口
@api.route('/address_list', methods=['POST','GET'])
def address_list():
    req_dict = request.values.to_dict()
    if req_dict is None:
        return jsonify(code=202,msg="参数错误")
    user_id=req_dict.get("user_id")
    if not user_id:
        return jsonify(code=201, msg="非法操作")

    try:
        addr_list=Address.query.filter(Address.user==user_id).all()
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(code=210, msg="查询地址信息异常")

    if addr_list:
        addrlists=[]
        for add in addr_list:
            addrlists.append(add.to_dict())
        return jsonify(code=200, msg="请求成功",data={"addrlists":addrlists})
    else:
        return jsonify(code=209, msg="数据为空",data=[])


# 查看地址接口
@api.route('/address_check', methods=['POST','GET'])
def address_check():
    req_dict = request.values.to_dict()
    if req_dict is None:
        return jsonify(code=202,msg="参数错误")
    addr_id=req_dict.get("addr_id")
    if not addr_id:
        return jsonify(code=201, msg="非法操作")

    try:
        addr=Address.query.filter(Address.id==addr_id).first()
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(code=210, msg="查询地址信息异常")

    if addr:
        return jsonify(code=200, msg="请求成功",data={"addr":addr.to_dict()})
    else:
        return jsonify(code=209, msg="数据为空",data=[])


# 修改收货地址
@api.route('/address_set', methods=['POST','GET'])
def address_set():
    req_dict = request.values.to_dict()
    if req_dict is None:
        return jsonify(code=202, msg="参数错误")
    addr_id=req_dict.get("id")
    user_id=req_dict.get("user_id")
    receiver=req_dict.get("receiver")
    pro_city_county=req_dict.get("pro_city_county")
    addr=req_dict.get("addr")
    phone=req_dict.get("phone")
    is_default=req_dict.get("is_default")

    if not all([addr_id,user_id,receiver,pro_city_county,addr,phone,is_default]):
        return jsonify(code=203, msg="参数不完整")

    if not re.match(r"1[34578]\d{9}", phone):
        return jsonify(code=204, msg="手机号格式不正确")

    print("-"*100)
    # 判断地址是否默认
    if is_default != "1":
        is_def="1"
        try:
            ad=Address.query.filter_by(user=user_id,is_default=is_def).first()
        except Exception as e:
            current_app.logger.error(e)
            return jsonify(code=210, msg="查询地址信息异常")

        if ad is None or ad['id']==addr_id:
            return jsonify(code=211,msg="请设置默认收货地址")

    # 查出修改的那一条地址
    try:
        data={
            "id":addr_id,
            "receiver":receiver,
            "pro_city_county":pro_city_county,
            "addr":addr,
            "phone":phone,
            "is_default":is_default
        }
        address = Address.query.filter(Address.id==addr_id).update(data)

        try:
            db.session.commit()
        except Exception as e:
            current_app.logger.error(e)
            db.session.rollback()

    except Exception as e:
        current_app.logger.error(e)
        return jsonify(code=210, msg="修改信息异常")

    if address:
        return jsonify(code=200, msg="修改成功")
    else:
        return jsonify(code=201, msg="非法操作")


# 删除收货地址
@api.route('/address_del', methods=['GET'])
def address_del():
    req_dict = request.values.to_dict()
    if req_dict is None:
        return jsonify(code=202, msg="参数错误")
    addr_id = req_dict.get("id")
    user_id = req_dict.get("user_id")
    if not all([addr_id,user_id]):
        return jsonify(code=203, msg="参数不完整")

    # 查询地址并判断
    try:
        addr_num=Address.query.filter_by(user=user_id).count()
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(code=210, msg="查询地址信息异常")
    if addr_num==1:
        return jsonify(code=212, msg="至少拥有一个收货地址")

    addr=Address.query.filter_by(id=addr_id).first()
    # if addr.is_default=="0":
    #     return jsonify(code=213, msg="默认地址不可删除")

    try:
        db.session.delete(addr)
        db.session.commit()
        return jsonify(code=200, msg="删除成功")
    except Exception as e:
        current_app.logger.error(e)
        db.session.rollback()
        return jsonify(code=201, msg="非法操作")


# 修改默认地址接口
@api.route('/def_address_set', methods=['POST','GET'])
def def_address_set():
    req_dict = request.values.to_dict()
    if req_dict is None:
        return jsonify(code=202, msg="参数错误")
    addr_id = req_dict.get("id")
    user_id = req_dict.get("user_id")
    if not all([addr_id,user_id]):
        return jsonify(code=203, msg="参数不完整")

    # 判断地址是否默认

    try:
        addr = Address.query.filter(Address.id==addr_id,Address.user==user_id)
        addr.update({"is_default": "0"})
        print("addr.first():%s" % addr.first())
        addr_list = Address.query.filter(Address.user==user_id).all()

        for add in addr_list:
            if add != addr.first():
                add.is_default="1"
                print("add:%s" % add)

        try:
            db.session.commit()
        except Exception as e:
            current_app.logger.error(e)
            db.session.rollback()
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(code=217, msg="修改信息异常")

    if addr:
        return jsonify(code=200, msg="修改成功")
    else:
        return jsonify(code=201, msg="非法操作")


# 默认地址接口
@api.route('/address_default', methods=['POST','GET'])
def addrs_default():
    req_dict = request.values.to_dict()
    if req_dict is None:
        return jsonify(code=202, msg="参数错误")
    user_id = req_dict.get("user_id")
    if not user_id:
        return jsonify(code=203, msg="参数不完整")

    try:
        ad = Address.query.filter_by(user=user_id, is_default=1).first()
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(code=210, msg="查询地址信息异常")
    if ad:
        return jsonify(code=200, msg="请求成功",data=ad.to_dict())
    else:
        return jsonify(code=209, msg="数据为空",data=[])


