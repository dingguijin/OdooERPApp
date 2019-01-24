# -*- coding: utf-8 -*-

import odoo
import odoo.modules.registry
import ast
from odoo import http
from odoo.http import request
from odoo.addons.web.controllers.main import Home


# 重写登录界面方法
class Home(Home):

    @http.route('/web/login', type='http', auth="none")
    def web_login(self, redirect=None, **kw):
        cr = request.cr
        uid = odoo.SUPERUSER_ID
        param_obj = request.env['ir.config_parameter']
        request.params['disable_footer'] = ast.literal_eval(param_obj.get_param('login_form_disable_footer')) or False
        request.params['disable_database_manager'] = ast.literal_eval(
            param_obj.get_param('login_form_disable_database_manager')) or False
        # 获取配置项的背景图
        request.params['background_src'] = param_obj.get_param('login_form_background_default') or ''
        return super(Home, self).web_login(redirect, **kw)
