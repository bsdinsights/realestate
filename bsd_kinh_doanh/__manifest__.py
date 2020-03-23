# -*- coding:utf-8 -*-
{
    'name': 'BSD Kinh doanh',
    'version': 'V0.1',
    'category': 'App',
    'author': 'Thịnh Lưu',
    'depends': [
                'base',
                'mail',
                'bsd_du_an',
    ],
    'data': [
        'security/user_groups.xml',
        'security/ir.model.access.csv',
        'security/bsd_security.xml',
        'views/res_partner_views.xml',
        'views/bsd_menu_item_views.xml',
    ],
    'application': True,
}