#coding=UTF-8

import datetime
import urllib
import requests
import hashlib
import xmltodict
import time
import random
import string


from danke.api_1_0.login import get_session_key
from danke.models import User, OrderInfo
from . import api
from flask import request, jsonify, json

from danke.constants import APP_ID, MCHID, KEY, NOTIFY_URL


# 生成订单号
def generate_out_trade_no():
    # 20位
    seeds = '1234567890'
    random_str = []
    for i in range(6):
        random_str.append(random.choice(seeds))
    subfix =  ''.join(random_str)

    return datetime.datetime.now().strftime("%Y%m%d%H%M%S") + subfix


# 生成nonce_str
def generate_randomStr():
    return ''.join(random.sample(string.ascii_letters + string.digits, 32))


# 生成签名
def generate_sign(param):
    stringA = ''

    ks = sorted(param.keys())
    # 参数排序
    for k in ks:
        stringA += (k + '=' + param[k] + '&')
    # 拼接商户KEY
    stringSignTemp = stringA + "key=" + KEY

    # md5加密
    hash_md5 = hashlib.md5(stringSignTemp.encode('utf8'))
    sign = hash_md5.hexdigest().upper()

    return sign


def MD5(str):
    md5 = hashlib.md5()
    md5.update(str.encode('utf-8'))
    print("md5:%s" % md5)
    return md5.hexdigest()


def formatBizQueryParaMap(paraMap, urlencode):
    """格式化参数，签名过程需要使用"""
    slist = sorted(paraMap)
    print("slist:%s" % slist)
    buff = []
    for k in slist:
        print("paraMap[k]:%s" % paraMap[k])
        print("urllib.quote(paraMap[k]):%s" % urllib.quote(paraMap[k]))
        v = urllib.quote(paraMap[k]) if urlencode else paraMap[k]
        print("v:%s" % v)
        buff.append("{0}={1}".format(k, v))
        print(buff)
    return "&".join(buff)


def getSign(obj):
    """生成签名"""
    # 签名步骤一：按字典序排序参数,formatBizQueryParaMap已做
    String = formatBizQueryParaMap(obj, False)
    print("String1:%s" % String)
    # 签名步骤二：在string后加入KEY
    String = "{0}&key={1}".format(String,KEY).encode("utf8")
    print("String2:%s" % String)
    # 签名步骤三：MD5加密
    String = hashlib.md5(String).hexdigest()
    print("String3:%s" % String)
    # 签名步骤四：所有字符转为大写
    result_ = String.upper()
    return result_


# 发送xml请求
def send_xml_request(url, param):
    # dict 2 xml
    # param = {'root': param}
    # print("param:%s" % param)
    # xml = xmltodict.unparse(param)
    xml=arrayToXml(param)
    print("xml:%s" % xml)
    response = requests.post(url, data=xml.encode('utf-8'), headers={'Content-Type': 'text/xml'})
    # xml 2 dict
    msg = response.text.encode('ISO-8859-1').decode('utf-8')
    print("msg:%s" % msg)
    xmlmsg = xmltodict.parse(msg)
    print("xmlmsg:%s" % xmlmsg)
    return xmlmsg


def arrayToXml(arr):
    """array转xml"""
    xml = ["<xml>"]
    for k, v in arr.iteritems():
        if v.isdigit():
            xml.append("<{0}>{1}</{0}>".format(k, v))
        else:
            xml.append("<{0}><![CDATA[{1}]]></{0}>".format(k, v))
    xml.append("</xml>")
    return "".join(xml)


# 支付接口
@api.route('/generate_bill', methods=['POST', 'GET'])
def generate_bill():
    req_dict = request.values.to_dict()
    if req_dict is None:
        return jsonify(code=202, msg="参数错误")
    fee = req_dict.get("fee")
    user_id = req_dict.get("user_id")
    order_id = req_dict.get("order_id")
    # res_dic = json.loads(get_session_key(code))
    # openid = res_dic.get("openid")

    user=User.query.filter_by(user_id=user_id).first()
    openid=user.openid
    print(openid)

    url = "https://api.mch.weixin.qq.com/pay/unifiedorder"
    order = OrderInfo.query.filter(OrderInfo.id == order_id).first()
    nonce_str = order.nonce_str		# 订单中加nonce_str字段记录（回调判断使用）
    print("nonce_str:%s" % nonce_str)

    out_trade_no = order.trade_no     # 支付单号，只能使用一次，不可重复支付
    print("out_trade_no:%s" % out_trade_no)
    # 1. 参数
    param = {
        "appid": APP_ID,
        "mch_id": MCHID,    # 商户号
        "nonce_str": nonce_str,     # 随机字符串
        "body": 'TEST_pay',     # 支付说明
        "out_trade_no": out_trade_no,   # 自己生成的订单号
        "total_fee": str(int(fee)*100),   # 标价金额（分）
        "spbill_create_ip": '127.0.0.1',    # 发起统一下单的ip
        "notify_url": NOTIFY_URL,
        "trade_type": 'JSAPI',      # 小程序写JSAPI
        "openid": openid,
    }
    print("param:%s" % param)
    # 2. 统一下单签名
    sign = getSign(param)
    print("sign:%s"% sign)
    param["sign"] = sign  # 加入签名
    print("param:%s" % param)
    # 3. 调用接口
    xmlmsg = send_xml_request(url, param)
    print("xmlmsg:%s" % xmlmsg)
    # 4. 获取prepay_id
    if xmlmsg['xml']['return_code'] == 'SUCCESS':
        print("1"*10)
        if xmlmsg['xml']['result_code'] == 'SUCCESS':
            print("1" * 10)
            prepay_id = xmlmsg['xml']['prepay_id']
            print("prepay_id:%s" % prepay_id)
            # 时间戳
            timeStamp = str(int(time.time()))
            print("timeStamp:%s" % timeStamp)
            # 5. 五个参数
            data = {
                "appId": APP_ID,
                "nonceStr": nonce_str,
                "package": "prepay_id=" + prepay_id,
                "signType": 'MD5',
                "timeStamp": timeStamp,
            }
            print("data:%s" % data)
            # 6. paySign签名
            paySign = getSign(data)
            print("paySign:%s" % paySign)
            data["paySign"] = paySign  # 加入签名
            print("data:%s" % data)
            # 7. 传给前端的签名后的参数
            return jsonify(code=200, msg="请求成功",data=data)
        else:
            msg = xmlmsg['xml']['err_code_des']
            return jsonify(code=202, msg=msg)
    else:
        msg = xmlmsg['xml']['return_msg']
        return jsonify(code=201, msg=msg)


