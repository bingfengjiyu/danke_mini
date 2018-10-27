# encoding: utf-8
"""
@author:YinLiang
@file: coupons.py
@time：2018/10/24 14:56
"""
import time

from datetime import datetime
from flask import request, jsonify, current_app

from danke import db
from danke.models import GoodsSku, DiscountCoupons, Coupons_user
from . import api


# 领取优惠券接口
@api.route('/get_mycoupons', methods=['POST','GET'])
def get_mycoupons():
    req_dict = request.values.to_dict()
    user_id = req_dict.get("user_id")
    coupons_id = req_dict.get("coupons_id")

    try:
        couponsuser=Coupons_user.query.filter(Coupons_user.user_id == user_id,Coupons_user.coupons_id==coupons_id).first()
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(code=210, msg="查询信息异常")

    if couponsuser:
        return jsonify(code=208, msg="重复领取")

    try:
        coupons_user=Coupons_user(user_id=user_id,coupons_id=coupons_id)

        db.session.add(coupons_user)
        db.session.commit()
        return jsonify(code=200, msg="领取成功")
    except Exception as e:
        current_app.logger.error(e)
        db.session.rollback()
        return jsonify(code=201, msg="领取失败")


# 我的优惠券接口
@api.route('/my_coupons', methods=['POST','GET'])
def my_coupons():
    req_dict = request.values.to_dict()
    user_id = req_dict.get("user_id")
    try:
        coupons_userlist=Coupons_user.query.filter(Coupons_user.user_id == user_id).all()
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(code=210, msg="查询信息异常")

    coupons_list=[]
    for coupons_user in coupons_userlist:
        try:
            coupons=DiscountCoupons.query.filter(DiscountCoupons.id == coupons_user.coupons_id).first()
        except Exception as e:
            current_app.logger.error(e)
            return jsonify(code=210, msg="查询信息异常")

        end_seconds = int(time.mktime(coupons.endtime.timetuple()))
        nowtime = int(time.mktime(datetime.now().timetuple()))
        if nowtime>end_seconds:
            is_expire = "1"   # 已过期
        else:
            is_expire = "0"   # 未过期
        coupons_dict=coupons.to_dict()
        coupons_dict["is_expire"]=is_expire
        coupons_dict["is_used"]=coupons_user.status
        coupons_list.append(coupons_dict)

    if coupons_list:
        return jsonify(code=200, msg="请求成功", data={"coupons_list": coupons_list})
    else:
        return jsonify(code=209, msg="数据为空", data={})


# 领券中心接口
@api.route('/get_couponslist', methods=['POST','GET'])
def get_couponslist():
    try:
        couponslist=DiscountCoupons.query.all()
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(code=210, msg="查询信息异常")

    coupons_list = []
    for coupons in couponslist:
        start_seconds = int(time.mktime(coupons.starttime.timetuple()))
        end_seconds = int(time.mktime(coupons.endtime.timetuple()))
        nowtime = int(time.mktime(datetime.now().timetuple()))
        # 有效期内
        if (nowtime < end_seconds) and (nowtime > start_seconds):
            coupons_list.append(coupons.to_dict())

    if coupons_list:
        return jsonify(code=200, msg="请求成功", data={"coupons_list": coupons_list})
    else:
        return jsonify(code=209, msg="数据为空", data=[])


# 订单页查询可用优惠券
@api.route('/usable_coupons', methods=['POST','GET'])
def usable_coupons():
    req_dict = request.values.to_dict()
    sku_id = req_dict.get("sku_id")
    user_id = req_dict.get("user_id")
    num = req_dict.get("num")   # 商品数量

    try:
        # 商品对象
        goods=GoodsSku.query.filter(GoodsSku.sku_id == sku_id).first()
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(code=210, msg="查询信息异常")
    total_price = goods.price_unit * int(num)
    coupons_list=[]
    for coupons in goods.coupons:
        print(coupons.id)
        try:
            # 领取优惠券的对象
            couponsuser=Coupons_user.query.filter(Coupons_user.user_id == user_id,Coupons_user.coupons_id == coupons.id).first()
        except Exception as e:
            current_app.logger.error(e)
            return jsonify(code=210, msg="查询信息异常")

        if couponsuser.status=="0":
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

            # 有效期内
            if (total_price > coupons.spendMoney) and (nowtime < end_seconds) and (nowtime > start_seconds):
                print("coupons.to_dict():%s" % coupons.to_dict())
                coupons_list.append(coupons.to_dict())

    if coupons_list:
        return jsonify(code=200, msg="请求成功", data={"coupons_list": coupons_list})
    else:
        return jsonify(code=209, msg="数据为空", data=[])





