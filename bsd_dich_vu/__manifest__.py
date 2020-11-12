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
        'data/bsd_automation_data.xml',
        'views/bsd_hop_dong_mua_ban_views.xml',
        'views/bsd_phu_luc_dong_so_huu_views.xml',
        'views/bsd_phu_luc_pttt_views.xml',
        'views/bsd_dien_tich_thuc_te_views.xml',
        'views/bsd_phu_luc_thay_doi_thong_tin_views.xml',
        'views/bsd_kh_ca_nhan_views.xml',
        'views/bsd_kh_doanh_nghiep_views.xml',
        'views/bsd_ps_gd_km_views.xml',
        'views/bsd_hd_ban_chuyen_nhuong_views.xml',
        'views/bsd_cn_dkbg_views.xml',
        'views/bsd_thong_bao_nghiem_thu_views.xml',
        'views/bsd_nghiem_thu_views.xml',
        'views/bsd_thong_bao_ban_giao_views.xml',
        'views/bsd_ban_giao_san_pham_views.xml',
        'views/bsd_ban_giao_giay_to_views.xml',
        'views/bsd_cn_ndc_views.xml',
        'views/bsd_thanh_ly_kt_hd_views.xml',
        'views/bsd_danh_sach_theo_doi_views.xml',
        'views/bsd_thong_bao_thanh_ly_views.xml',
        'views/bsd_thanh_ly_views.xml',
        'views/bsd_thong_bao_thanh_toan_views.xml',
        'views/bsd_thong_bao_nhac_no_views.xml',
        'views/bsd_dat_coc_views.xml',
        'wizards/bsd_wizard_tao_thong_bao_tt_nn_views.xml',
        'views/bsd_menu_item_views.xml',
        'views/product_template_views.xml',
        'wizards/bsd_wizard_hd_ban_views.xml',
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
        'wizards/bsd_wizard_tb_bg_views.xml',
        'wizards/bsd_wizard_nghiem_thu_views.xml',
        'wizards/bsd_wizard_bg_sp_views.xml',
        'wizards/bsd_wizard_cn_ndc_views.xml',
        'wizards/bsd_wizard_bg_gt_views.xml',
        'wizards/bsd_wizard_tl_kt_hd_views.xml',
        'wizards/bsd_wizard_ds_td_views.xml',
        'wizards/bsd_wizard_tb_tl_views.xml',
        'wizards/bsd_wizard_thanh_ly_views.xml',
        'reports/report_bsd_uoc_tinh_views.xml',
        'reports/report_bsd_hd_ban_views.xml',
        'reports/report_bsd_hd_ban_cn_views.xml',
        'reports/report_bsd_tb_nt_views.xml',
        'reports/report_bsd_nghiem_thu_views.xml',
        'reports/report_bsd_tb_bg_views.xml',
        'reports/report_bsd_bg_sp_views.xml',
        'reports/report_bsd_bg_gt_views.xml',
        'reports/report_bsd_tl_kt_hd_views.xml',
        'reports/report_bsd_tb_tl_views.xml',
        'reports/report_bsd_thanh_ly_views.xml',
        'reports/report_bsd_tb_tt_nn_views.xml',
        'reports/report_bsd_tb_nhac_no_views.xml',
        'views/assets.xml',
    ],
    'application': True,
    'qweb': ['static/xml/*.xml'],
}
