# -*- coding: utf-8 -*-
{
    'name': "数据库过期解决",

    'summary': """
    安装此模块可以解决提示数据库已过期**天的问题，支持版本（10，11，12）
    """,

    'description': """
    安装完成后，在系统的hosts文件中加入一行
    "odoo.com     127.0.0.1"
    """,

    'author': "SuXueFeng",
    'website': "https://www.sxfblog.com",

    'category': 'database',
    'version': '1.0',
    'depends': ['base'],
    'installable': True,
    'application': False,
    'auto_install': False,
    'data': [
        'data/database.xml',
    ],

}
