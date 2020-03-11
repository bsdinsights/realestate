# -*- coding:utf-8 -*-
{
    'name': 'BSD Quản lý dự án',
    'version': 'V0.1',
    'category': 'App',
    'author': 'Thịnh Lưu',
    'depends': [
                'base',
                'mail'
    ],
    'data': [
        'security/user_groups.xml',
        'security/ir.model.access.csv',
        'security/bsd_security.xml',
        'views/bsd_du_an_views.xml',
        'views/bsd_toa_nha_views.xml',
        'views/bsd_tang_views.xml',
        'views/bsd_menu_item_views.xml'
    ],
    'application': True,
}