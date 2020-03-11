# -*- coding:utf-8 -*-
{
    'name': 'BSD Danh mục',
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
        'views/bsd_quoc_gia_views.xml',
        'views/bsd_tinh_thanh_views.xml',
        'views/bsd_quan_huyen_views.xml',
        'views/bsd_menu_item_views.xml'
    ],
    'application': True,
}