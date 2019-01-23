# -*- coding: utf-8 -*-
import logging
from odoo import api, fields, models

_logger = logging.getLogger(__name__)


class RPCBaseConfig(models.TransientModel):
    _name = 'rpc.base.config'
    _description = u"基础配置"
    _inherit = 'res.config.settings'

    rpc_url = fields.Char(string=u'RPC连接地址')
    rpc_db = fields.Char(string=u'RPC连接数据库')
    username = fields.Char(string=u'RPC连接用户名')
    password = fields.Char(string=u'RPC连接密码')

    @api.multi
    def get_default_params(self, fields):
        ir_values = self.env['ir.values']
        return {
            'rpc_url': ir_values.get_default('rpc.base.config', 'rpc_url') or 'http://demo.odoo.com',
            'rpc_db': ir_values.get_default('rpc.base.config', 'rpc_db') or 'demo',
            'username': ir_values.get_default('rpc.base.config', 'username') or 'demo',
            'password': ir_values.get_default('rpc.base.config', 'password') or 'demo',
        }

    @api.multi
    def set_rpc_url(self):
        self.ensure_one()
        return self.env['ir.values'].sudo().set_default('rpc.base.config', 'rpc_url', self.rpc_url)

    @api.multi
    def set_rpc_db(self):
        self.ensure_one()
        return self.env['ir.values'].sudo().set_default('rpc.base.config', 'rpc_db', self.rpc_db)

    @api.multi
    def set_username(self):
        self.ensure_one()
        return self.env['ir.values'].sudo().set_default('rpc.base.config', 'username', self.username)

    @api.multi
    def set_password(self):
        self.ensure_one()
        return self.env['ir.values'].sudo().set_default('rpc.base.config', 'password', self.password)
