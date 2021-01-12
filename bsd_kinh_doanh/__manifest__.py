# -*- coding:utf-8 -*-
{
    'name': 'BSD Kinh doanh',
    'version': 'V0.1',
    'category': 'App',
    'author': 'Thịnh Lưu',
    'depends': [
                'base',
                'mail',
                'hr',
                'bsd_du_an',
                'bsd_danh_muc',
                'base_automation',
    ],
    'data': [
        'security/user_groups.xml',
        'security/ir.model.access.csv',
        'security/bsd_security.xml',
        'views/assets.xml',
        'views/bsd_kh_ca_nhan_views.xml',
        'views/bsd_kh_doanh_nghiep_views.xml',
        'views/bsd_dot_mo_ban_views.xml',
        'views/bsd_product_template_views.xml',
        'views/bsd_giu_cho_thien_chi_views.xml',
        'views/bsd_rap_can_views.xml',
        'views/bsd_giu_cho_views.xml',
        'views/bsd_khuyen_mai_views.xml',
        'views/bsd_bao_gia_views.xml',
        'views/bsd_dieu_kien_ban_giao_views.xml',
        'views/bsd_dat_coc_views.xml',
        'views/bsd_dat_coc_td_tt_views.xml',
        'views/bsd_chuyen_gc_views.xml',
        'views/bsd_huy_gc_views.xml',
        'views/bsd_thu_hoi_views.xml',
        'views/bsd_them_unit_views.xml',
        'views/bsd_chiet_khau_dac_biet_views.xml',
        'views/bsd_chiet_khau_chung_views.xml',
        'views/bsd_quan_tam_views.xml',
        'views/bsd_lich_thanh_toan_views.xml',
        'views/bsd_dat_coc_chuyen_dd_views.xml',
        'views/bsd_gia_han_gc_views.xml',
        'views/bsd_tinh_hoa_hong_views.xml',
        'views/bsd_chuyen_ut_gc_views.xml',
        'views/bsd_menu_item_views.xml',
        'data/bsd_automation_data.xml',
        'data/bsd_sequence_data.xml',
        'data/bsd_kh_dn_data.xml',
        'wizards/bsd_wizard_bao_gia_views.xml',
        'wizards/bsd_wizard_dc_views.xml',
        'wizards/bsd_wizard_chuyen_gc_views.xml',
        'wizards/bsd_wizard_thu_hoi_views.xml',
        'wizards/bsd_wizard_them_unit_views.xml',
        'wizards/bsd_wizard_huy_gc_views.xml',
        'wizards/bsd_wizard_chiet_khau_dac_biet_views.xml',
        'wizards/bsd_wizard_dot_mb_views.xml',
        'wizards/bsd_wizard_assign_kh_views.xml',
        'reports/report_bsd_gc_tc_views.xml',
        'reports/report_bsd_giu_cho_views.xml',
        'reports/report_bsd_bao_gia_views.xml',
        'reports/report_bsd_dat_coc_views.xml',
        'views/bsd_du_an_views.xml'
    ],
    'application': True,
}