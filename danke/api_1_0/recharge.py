# encoding: utf-8
"""
@author:YinLiang
@file: recharge.py
@time：2018/10/23 11:03
"""
import hashlib
import time

import datetime
import requests
from flask import request

from danke.api_1_0 import api
from danke.api_1_0.pay import formatBizQueryParaMap, send_xml_request, generate_out_trade_no


@api.route('/recharge', methods=['POST', 'GET'])
def Recharge():
    req_dict = request.values.to_dict()
    productid=req_dict.get("productid")
    phonenum=req_dict.get("phonenum")
    url="http://test.saiheyi.com/Stock/Post"
    actionname="recharge"
    timestamp=time.strftime("%Y-%m-%d %H:%M:%S")
    print("timestamp:%s" % timestamp)
    partnerid="102964"
    stockordernumber=generate_out_trade_no()

    data={
        "productid":productid,
        "phonenum":phonenum,
        "actionname":actionname,
        "timestamp":timestamp,
        "partnerid":partnerid,
        "stockordernumber":stockordernumber
    }
    sign=get_Sign(data)
    data["sign"]=sign
    # str = formatBizQueryParaMap(data, False)
    # string = "{0}".format(str).encode("utf8")
    # print("string:%s" % string)
    # response = requests.post(url, data=string, headers={'Content-Type': 'application/x-www-form-urlencoded'})

    headers = {"Content-type": "application/x-www-form-urlencoded; charset=UTF-8",
               "Accept": "*/*"}
    params = {'username': 'xxxx'}
    data = urllib.urlencode(params)

    conn = httplib.HTTPConnection(host)
    conn.request('POST', url, data, headers)

    msg = response.text
    print(msg)
    return msg




def get_Sign(data):
    str=formatBizQueryParaMap(data, False)
    signkey = "C7FA8FC2D9256DD6865ADFFA81249FEC"
    str="{0}{1}".format(str,signkey).encode("utf8")
    print("str:%s" % str)
    String = hashlib.md5(str).hexdigest()
    print("String:%s" % String)
    return String.upper()











