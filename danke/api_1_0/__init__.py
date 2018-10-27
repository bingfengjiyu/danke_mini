# coding:utf-8

from flask import Blueprint

api=Blueprint("api_1_0",__name__,template_folder='../../templates')

from . import index,address,goods,login,upload,admin,group,orders,pay,payback_demo,recharge,coupons
