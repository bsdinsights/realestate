# -*- coding:utf-8 -*-
{
    'name': 'BSD Dịch vụ',
    'version': 'V0.1',
    'category': 'App',
    'author': 'Thịnh Lưu',
    'depends': [
                'base',
                'mail',
                'bsd_kinh_doanh',
                'bsd_du_an',
                'bsd_danh_muc',
    ],
    'data': [
        'security/user_groups.xml',
        'security/ir.model.access.csv',
        'security/bsd_security.xml',
        'views/bsd_hop_dong_mua_ban_views.xml',
        'views/bsd_phu_luc_dong_so_huu_views.xml',
        'views/bsd_menu_item_views.xml',
        'wizards/bsd_wizard_ky_hdb_views.xml',
        'wizards/bsd_wizard_ky_pl_dsh_views.xml',

    ],
    'application': True,
}