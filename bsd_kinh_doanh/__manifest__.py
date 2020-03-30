# -*- coding:utf-8 -*-
{
    'name': 'BSD Kinh doanh',
    'version': 'V0.1',
    'category': 'App',
    'author': 'Thịnh Lưu',
    'depends': [
                'base',
                'mail',
                'crm',
                'bsd_du_an',
                'bsd_danh_muc',
    ],
    'data': [
        'security/user_groups.xml',
        'security/ir.model.access.csv',
        'security/bsd_security.xml',
        'views/res_partner_views.xml',
        'views/bsd_dot_mo_ban_views.xml',
        'views/bsd_product_template_views.xml',
        'views/bsd_giu_cho_thien_chi_views.xml',
        'views/bsd_rap_can_views.xml',
        'views/bsd_giu_cho_views.xml',
        'views/bsd_menu_item_views.xml',
        'data/bsd_automation_data.xml',
    ],
    'application': True,
}