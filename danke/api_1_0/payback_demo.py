#coding=UTF-8
'''
统一下单回调处理
'''

import xmltodict
from flask import Response, request

from danke.models import OrderInfo
from . import api


@api.route('/notifyurl', methods=['POST','GET'])
def payback():
    # msg = request.body.decode('utf-8')
    # xmlmsg = xmltodict.parse(msg)
    xml_str = request.data
    print("payback_xml_str:%s" % xml_str)
    xmlmsg = xmltodict.parse(xml_str)
    print("payback_xmlmsg:%s" % xmlmsg)
    return_code = xmlmsg['xml']['return_code']
    print("return_code:%s" % return_code)
    if return_code == 'FAIL':
        # 官方发出错误
        return Response("""<xml><return_code><![CDATA[FAIL]]></return_code>
                            <return_msg><![CDATA[Signature_Error]]></return_msg></xml>""",
                        mimetype='application/xml', status=200)
    elif return_code == 'SUCCESS':
        # 拿到这次支付的订单号
        out_trade_no = xmlmsg['xml']['out_trade_no']
        order=OrderInfo.query.filter(OrderInfo.trade_no == out_trade_no).first()
        if xmlmsg['xml']['nonce_str'] != order.nonce_str:

            # 随机字符串不一致
            return Response("""<xml><return_code><![CDATA[FAIL]]></return_code>
                                        <return_msg><![CDATA[Signature_Error]]></return_msg></xml>""",
                            mimetype='application/xml', status=200)

        # 根据需要处理业务逻辑
        return Response("""<xml><return_code><![CDATA[SUCCESS]]></return_code>
                            <return_msg><![CDATA[OK]]></return_msg></xml>""",
                        mimetype='application/xml', status=200)