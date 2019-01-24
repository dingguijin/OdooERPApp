# -*- encoding: utf-8 -*-
{
    'name': ' 美化用户登录界面',
    'summary': '美化了odoo10登录界面',
    'version': '10.0.1.1',
    'category': 'Website',
    'summary': """美化了odoo10登录界面""",
    'author': "SuXueFeng",
    'website': 'https://sxfblog.com',
    'depends': ['base'],
    'data': [
        'data/ir_config_parameter.xml',
        'views/login_templates.xml',
    ],
    'installable': True,
    'application': True,
}
