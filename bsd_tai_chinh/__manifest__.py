# -*- coding:utf-8 -*-
{
    'name': 'BSD Tài Chính',
    'version': 'V0.1',
    'category': 'App',
    'author': 'Thịnh Lưu',
    'depends': [
                'base',
                'mail',
                'bsd_du_an',
                'bsd_danh_muc',
                'bsd_kinh_doanh',
                'bsd_dich_vu',
    ],
    'data': [
        'security/user_groups.xml',
        'security/ir.model.access.csv',
        'security/bsd_security.xml',
        'views/bsd_phieu_thu_views.xml',
        'views/bsd_cong_no_views.xml',
        'views/bsd_cong_no_ct_views.xml',
        'views/bsd_menu_item_views.xml',
        'views/bsd_giu_cho_thien_chi_views.xml',
        'views/bsd_giu_cho_views.xml',
        'views/bsd_dat_coc_views.xml',
        'views/bsd_lich_thanh_toan_views.xml',
    ],
    'application': True,
}