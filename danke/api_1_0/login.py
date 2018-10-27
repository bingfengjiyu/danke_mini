# coding:utf-8
import re

import requests
import base64

from flask import json
from flask import session,request,jsonify,current_app
from danke.models import User,Address, Goods, GoodsType, GoodsSku
from . import api
from danke import db,models,constants,redis_store


# 获取openid
def get_session_key(code):
    app_id = constants.APP_ID
    secret = constants.SECRET
    print("code:%s" % code)
    url = 'https://api.weixin.qq.com/sns/jscode2session?appid=%s&secret=%s&js_code=%s&grant_type=authorization_code' % (app_id, secret, code)
    r = requests.get(url)
    result = r.text
    print("result:%s" % result)
    return result


# 登陆
@api.route('/login', methods=['POST','GET'])
def login():
    req_dict = request.values.to_dict()
    if req_dict is None:
        return jsonify(code=201,msg="参数错误")
    code = req_dict.get("code")
    name = req_dict.get("name")
    avatar_url = req_dict.get("avatar_url")
    if not all([code,name,avatar_url]):
        return jsonify(code=202,msg="参数不完整",data='')
    res_dic = json.loads(get_session_key(code))
    try:
        openid = res_dic.get("openid")
        print("openid:%s" % openid)
    except Exception as e:
        current_app.logger.error(e)

    try:
        user = User.query.filter_by(openid=openid).first()
        print(user)
    except Exception as e:
        current_app.logger.error(e)

    # 如果用户存在
    if user:
        return jsonify(code=200, msg="授权成功", data=user.to_dict())
    else:
        # 用户不存在
        u = User(openid=openid, name=name, avatar_url=avatar_url)
        try:
            db.session.add(u)
            db.session.commit()
        except Exception as e:
            current_app.logger.error(e)
            db.session.rollback()
            return jsonify(code=205, msg="数据异常", data="")

        try:
            user = User.query.filter_by(openid=openid).first()
        except Exception as e:
            current_app.logger.error(e)

        return jsonify(code=200, msg="授权成功", data=user.to_dict())


# 测试登陆接口
@api.route('/adduser', methods=['POST','GET'])
def adduser():
    req_dict = request.values.to_dict()
    if req_dict is None:
        return jsonify(code=201, msg="参数错误")
    openid = req_dict.get("openid")
    name = base64.b64encode(req_dict.get("name"))
    mobile=req_dict.get("mobile")
    avatar_url = req_dict.get("avatar_url")
    u = User(openid=openid, mobile=mobile, name=name, avatar_url=avatar_url)
    try:
        db.session.add(u)
        db.session.commit()
    except Exception as e:
        current_app.logger.error(e)
        db.session.rollback()
        resp = {
            "code": 201,
            "msg": "数据异常",
            "data": ''
        }
        return jsonify(resp)

    data = {
        "openid": openid,
        "name": name,
        "avatar_url": avatar_url
    }

    return jsonify(code=200, msg="授权成功", data=data)

