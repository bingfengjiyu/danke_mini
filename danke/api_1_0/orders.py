# encoding: utf-8
"""
@author:YinLiang
@file: orders.py
@time：2018/10/12 16:01
"""
import datetime
from time import strptime

from danke import db
from danke.api_1_0.pay import generate_out_trade_no, generate_randomStr
from danke.models import Groupadd, OrderInfo, Group_user, GoodsSku, DiscountCoupons, User, Coupons_user
from . import api
from flask import request,jsonify,current_app


# 生成订单接口
@api.route('/order_add', methods=['POST','GET'])
def order_add():
    req_dict = request.values.to_dict()

    if req_dict is None:
        return jsonify(code=202, msg="参数错误")
    user_id = req_dict.get("user_id")
    sku_id = req_dict.get("sku_id")
    addr_id = req_dict.get("addr_id")
    coupons_id = req_dict.get("coupons_id")     # 拼团或套餐，优惠券id为0
    total_count = req_dict.get("total_count")
    parent = req_dict.get("parent")
    type = req_dict.get("type")             # 拼团类型
    group_id = req_dict.get("group_id")     # 如果是团长，group_id为0

    if not all([user_id, sku_id, addr_id, coupons_id, total_count]):
        return jsonify(code=203, msg="参数不完整")

    good=GoodsSku.query.filter(GoodsSku.sku_id == sku_id).first()
    group_num = good.pnum
    price = good.group_price
    total_price=int(total_count)*price
    out_trade_no = generate_out_trade_no()      # 交易编号
    nonce_str = generate_randomStr()            # 随机字符串

    # 单独购买
    if parent == "0" and group_id == "0" and type == "1":
        try:
            # 减去优惠券的价格
            coupons = DiscountCoupons.query.filter(DiscountCoupons.id == coupons_id).first()
            coupons_price = coupons.price
            total_price=total_price-coupons_price

            order = OrderInfo(user_id=user_id, addr_id=addr_id, sku_id=sku_id, type=type,coupons_id=coupons_id,total_count=total_count, total_price=total_price,trade_no=out_trade_no,nonce_str=nonce_str)
        except Exception as e:
            return jsonify(code=207, msg="数据异常")

        try:
            db.session.add(order)
            db.session.commit()
            change_coupons(user_id, coupons)
            return jsonify(code=200, msg="购买成功")
        except Exception as e:
            current_app.logger.error(e)
            db.session.rollback()
            return jsonify(code=201, msg="非法操作")

    else:

        # 团长开团
        if parent == "0" and group_id == "0" and type == "2":
            try:
                group = Groupadd(group_num=group_num)
                db.session.add(group)
                db.session.flush()
            except Exception as e:
                return jsonify(code=207, msg="数据异常")

            g_id = group.id
            try:
                groupadd=Groupadd.query.filter(Groupadd.id == g_id).first()
                groupadd.ptetime=(groupadd.create_time+datetime.timedelta(days=1))

            except Exception as e:
                return jsonify(code=207, msg="数据异常")

            try:
                db.session.commit()
            except Exception as e:
                current_app.logger.error(e)
                db.session.rollback()

        # 团员参团
        elif parent == "1" and type == "3":
            g_id = group_id
            gro = Group_user.query.filter(Group_user.group_id == g_id)
            for g in gro.all():
                if int(user_id) == g.user_id:
                    return jsonify(code=219, msg="您已经在拼团中")
            if gro.count() >= int(group_num):
                return jsonify(code=218, msg="团员已满,请重新开团")

        try:
            try:
                order = OrderInfo(user_id=user_id, addr_id=addr_id, sku_id=sku_id, group_id=g_id, type=type,total_count=total_count, total_price=total_price, parent=parent,trade_no=out_trade_no,nonce_str=nonce_str)
            except Exception as e:
                return jsonify(code=207, msg="数据异常")

            try:
                groupuser = Group_user(user_id=user_id, group_id=g_id)
            except Exception as e:
                return jsonify(code=207, msg="数据异常")

            db.session.add(order)
            db.session.add(groupuser)
            db.session.commit()

            # 使用优惠券
            # remove_coupons(user_id,coupons)

            gro = Group_user.query.filter(Group_user.group_id == g_id)
            if gro.count() == int(group_num):
                groupadd = Groupadd.query.filter(Groupadd.id == g_id).first()
                groupadd.status="1"
                try:

                    db.session.commit()
                    return jsonify(code=200, msg="拼团成功,团员已满")
                except Exception as e:
                    current_app.logger.error(e)
                    db.session.rollback()
                    return jsonify(code=201, msg="非法操作")
            else:
                num = int(group_num) - gro.count()
                return jsonify(code=200, msg="拼团成功,还差%s人" % num)

        except Exception as e:
            current_app.logger.error(e)
            db.session.rollback()
            return jsonify(code=201, msg="非法操作")


def change_coupons(user_id,coupons):
    try:
        coupons_user = Coupons_user.query.filter(Coupons_user.user_id == user_id,Coupons_user.coupons_id == coupons.id).update({"status":"1"})

        db.session.commit()
    except Exception as e:
        current_app.logger.error(e)
        db.session.rollback()
        return jsonify(code=201, msg="非法操作")



