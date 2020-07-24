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
        'views/bsd_dien_tich_thuc_te_views.xml',
        'views/bsd_phu_luc_thay_doi_thong_tin_views.xml',
        'views/bsd_kh_ca_nhan_views.xml',
        'views/bsd_ps_gd_km_views.xml',
        'views/bsd_hd_ban_chuyen_nhuong_views.xml',
        'views/bsd_cn_dkbg_views.xml',
        'views/bsd_thong_bao_nghiem_thu_views.xml',
        'views/bsd_nghiem_thu_views.xml',
        'views/bsd_menu_item_views.xml',
        'views/product_template_views.xml',
        'wizards/bsd_wizard_ky_hdb_views.xml',
        'wizards/bsd_wizard_ky_pl_dsh_views.xml',
        'wizards/bsd_wizard_ky_pl_tti_views.xml',
        'wizards/bsd_wizard_ms_hdb_views.xml',
        'wizards/bsd_wizard_uoc_tinh_ck_tt_views.xml',
        'wizards/bsd_wizard_khong_duyet_gd_km_views.xml',
        'wizards/bsd_wizard_ky_ttdc_views.xml',
        'wizards/bsd_wizard_khong_duyet_hd_ban_cn_views.xml',
        'wizards/bsd_wizard_khong_duyet_cn_dkbg_views.xml',
        'wizards/bsd_wizard_ds_tb_views.xml',
        'wizards/bsd_wizard_tb_nt_views.xml',
        'wizards/bsd_wizard_nghiem_thu_views.xml',
        'reports/report_bsd_uoc_tinh_views.xml',
        'reports/report_bsd_hd_ban_views.xml',
        'reports/report_bsd_hd_ban_cn_views.xml',
        'reports/report_bsd_tb_nt_views.xml',
        'reports/report_bsd_nghiem_thu_views.xml',
    ],
    'application': True,
}