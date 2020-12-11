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
        'views/bsd_can_tru_views.xml',
        'views/bsd_hoan_tien_views.xml',
        'views/bsd_chiet_khau_giao_dich_views.xml',
        'views/bsd_phi_phat_sinh_views.xml',
        'views/bsd_lai_phat_views.xml',
        'views/bsd_cn_qsdd_views.xml',
        'views/bsd_menu_item_views.xml',
        'views/bsd_giu_cho_thien_chi_views.xml',
        'views/bsd_giu_cho_views.xml',
        'views/bsd_dat_coc_views.xml',
        'views/bsd_lich_thanh_toan_views.xml',
        'views/bsd_hd_ban_views.xml',
        'views/bsd_huy_gc_views.xml',
        'views/bsd_nghiem_thu_views.xml',
        'wizards/bsd_wizard_ut_lp_views.xml',
        'wizards/bsd_wizard_cn_qsdd_views.xml',
        'wizards/bsd_wizard_tt_dot_views.xml',
        'wizards/bsd_wizard_tt_gc_tc_views.xml',
        'wizards/bsd_wizard_tt_giu_cho_views.xml',
        'wizards/bsd_wizard_tt_dat_coc_views.xml',
        'reports/report_bsd_phieu_thu_views.xml',
        'reports/report_bsd_hoan_tien_views.xml',
        'reports/report_bsd_uoc_tinh_lp_views.xml',
        'views/assets.xml'
    ],
    'application': True,
    'qweb': ['static/xml/*.xml'],
}
