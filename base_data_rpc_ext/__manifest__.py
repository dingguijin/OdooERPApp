# -*- coding: utf-8 -*-
{
    'name': "数据同步-RPC",
    'summary': """rpc方式进行基础数据同步""",
    'description': """rpc方式进行基础数据同步 """,
    'author': "li",
    'website': "",
    'category': 'rpc',
    'version': '0.1',
    'depends': ['base', 'base_data_rpc'],
    'installable': True,
    'application': True,
    'auto_install': False,
    'data': [
        'security/ir.model.access.csv',
        'views/data_uploading.xml',
    ],
    'qweb': [
    ],
}
