# -*- coding: utf-8 -*-
from odoo import fields, models, api, _
import logging

_logger = logging.getLogger(__name__)


class TestModel1(models.Model):
    _name = 'rpc.test1'
    _rec_name = 'name'
    _description = u"测试模型1"

    name = fields.Char(string=u'名称')
    ttt = fields.Char(string=u'测试字段1')
    login = fields.Char(string=u'登录名称')
    password = fields.Char(string=u'登录密码')
    password_crypt = fields.Char(string=u'登录密码')

