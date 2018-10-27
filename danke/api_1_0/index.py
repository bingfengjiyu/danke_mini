# coding:utf-8

from . import api


@api.route('/getinfo')
def hello_world():
    return 'Hello World!'




