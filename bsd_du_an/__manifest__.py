# -*- coding:utf-8 -*-
{
    'name': 'BSD Quản lý dự án',
    'version': 'V0.1',
    'category': 'App',
    'author': 'Thịnh Lưu',
    'depends': [
                'base',
                'mail',
                'product',
                'l10n_vn',
    ],
    'data': [
        'security/user_groups.xml',
        'security/ir.model.access.csv',
        'security/bsd_security.xml',
        'views/bsd_du_an_views.xml',
        'views/bsd_toa_nha_views.xml',
        'views/bsd_tang_views.xml',
        'views/bsd_product_template_views.xml',
        'views/bsd_loai_san_pham_views.xml',
        'views/bsd_thong_tin_ky_thuat_views.xml',
        'views/bsd_menu_item_views.xml',
        'wizards/message_wizard_views.xml'
    ],
    'application': True,
}