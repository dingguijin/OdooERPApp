# -*- coding: utf-8 -*-
import logging
import xmlrpclib
from ast import literal_eval
from odoo.exceptions import UserError
import sys

from odoo.http import request

reload(sys)
sys.setdefaultencoding('utf-8')


def get_rpc_condif():
    """获取rpc配置项中的各项配置
    :return url, db, username, pwd
    """
    rpc_url = request.env['ir.values'].get_default('rpc.base.config', 'rpc_url')
    rpc_db = request.env['ir.values'].get_default('rpc.base.config', 'rpc_db')
    username = request.env['ir.values'].get_default('rpc.base.config', 'username')
    password = request.env['ir.values'].get_default('rpc.base.config', 'password')
    if rpc_url and rpc_db and username and password:
        return rpc_url, rpc_db, username, password
    else:
        raise UserError(u"请先配置RPC参数！")


def connection_rpc(rpc_url, rpc_db, username, password):
    """开始连接rpc
    :param rpc_url: url地址
    :param rpc_db: 数据库
    :param username： 登录用户名
    :param password： 登录用户密码
    :return 连接实例和登录用户的uid
    """
    try:
        common = xmlrpclib.ServerProxy('{}/xmlrpc/2/common'.format(rpc_url))
        uid = common.authenticate(rpc_db, username, password, {})
        model = xmlrpclib.ServerProxy('{}/xmlrpc/2/object'.format(rpc_url))
    except Exception as e:
        logging.info(u"连接RPC发生错误！错误原因:{}".format(e))
        raise UserError(u"连接RPC发生错误！错误原因:{}".format(e))
    logging.info(common.version())
    return model, uid


def search_read(models, rpc_db, uid, pwd, model_name, domain, fields_dict):
    """根据数据表查找和获取数据
    :param models: 远程模型实例
    :param rpc_db: 数据库
    :param uid: 登录用户id
    :param pwd: 登录用户密码
    :param model_name: 操作模型名称
    :param domain: 条件(list)
    :param fields_dict: 字段字典
    :return list 返回获取到的结果
    """
    try:
        return models.execute_kw(rpc_db, uid, pwd, model_name, 'search_read', [domain], fields_dict)
    except Exception as e:
        logging.info(u"获取指定数据表数据时发生错误！特别注意条件规则表达式,\r\n具体错误原因:{}".format(e))
        raise UserError(u"获取指定数据表数据时发生错误！特别注意条件规则表达式,\r\n具体错误原因:{}".format(e))


def string_transfer_list(str_list):
    try:
        return literal_eval(str_list)
    except SyntaxError:
        raise UserError(u"转换条件表达式失败！{},条件表达式格式为：['name', '=', 'admin']".format(str_list))
