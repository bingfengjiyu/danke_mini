# encoding: utf-8
"""
@author:YinLiang
@file: group.py
@time：2018/10/10 11:59
"""

from danke.models import Groupadd, OrderInfo, User
from . import api
from flask import request,jsonify,current_app


# 查询拼团信息接口
@api.route('/group_list', methods=['POST','GET'])
def group_list():
    req_dict = request.values.to_dict()

    sku_id = req_dict.get("sku_id")
    if not sku_id:
        return jsonify(code=201, msg="非法操作")
    try:
        order_list = OrderInfo.query.filter(OrderInfo.sku_id == sku_id,OrderInfo.parent=="0",OrderInfo.type=="2").all()
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(code=210, msg="查询信息异常")

    if order_list:
        order_lists = []
        i=0
        for order in order_list:
            if i == 2:
                break
            print("-"*10)
            print(order.id)
            user=User.query.filter(User.user_id == order.user_id).first()
            group=Groupadd.query.filter(Groupadd.id == order.group_id,Groupadd.status=="0").first()
            groupdict = group.to_dict()
            groupdict["user"] = user.to_getinfo()
            order_lists.append(groupdict)
            i += 1
            # if order.to_getgroup():
            #     if i==2:
            #         break
            #     order_lists.append(order.to_getgroup())
            #     i+=1

        return jsonify(code=200, msg="请求成功", data={"order_lists": order_lists})
    else:
        return jsonify(code=209, msg="数据为空", data=[])



