# -*- coding:utf-8 -*-
{
    'name': 'BSD Danh mục',
    'version': 'V0.1',
    'category': 'App',
    'author': 'Thịnh Lưu',
    'depends': [
                'base',
                'mail',
                'account',
                'bsd_du_an',
    ],
    'data': [
        'security/user_groups.xml',
        'security/ir.model.access.csv',
        'security/bsd_security.xml',
        'views/bsd_quoc_gia_views.xml',
        'views/bsd_tinh_thanh_views.xml',
        'views/bsd_quan_huyen_views.xml',
        'views/bsd_phuong_xa_views.xml',
        'views/bsd_lai_suat_views.xml',
        'views/bsd_dieu_kien_ban_giao_views.xml',
        'views/bsd_phuong_thuc_thanh_toan_views.xml',

        'views/bsd_menu_item_views.xml'
    ],
    'application': True,
}