# -*- coding: utf-8 -*-
{
    'name': "数据同步-RPC",
    'summary': """rpc方式进行基础数据同步""",
    'description': """rpc方式进行基础数据同步 """,
    'author': "SuXueFeng",
    'website': "http://www.sxfblog.com",
    'category': 'rpc',
    'version': '0.1',
    'depends': ['base'],
    'installable': True,
    'application': True,
    'auto_install': False,
    'data': [
        'security/ir.model.access.csv',
        'groups/rpc_groups.xml',
        'views/menu.xml',
        'views/dash_board.xml',
        'views/base_config.xml',
        'views/base_data.xml',
        'views/data_synchronization.xml',
    ],
    'qweb': [
        'static/src/xml/dash_board.xml',
    ],
}
