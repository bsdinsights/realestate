# -*- coding:utf-8 -*-
{
    'name': 'BSD Giỏ hàng',
    'version': '0.1',
    'category': 'App',
    'author': 'Thịnh Lưu',
    'depends': [
                'base',
                'bsd_du_an',
                'bsd_kinh_doanh',
    ],
    'data': [
        'views/assets.xml',
        'views/sale_chart_views.xml',
        'views/bsd_giu_cho_views.xml',
        'views/bsd_unit_views.xml',
        'views/bsd_bao_gia_views.xml',
        'views/bsd_quan_tam_views.xml',
    ],
    'qweb': ['static/xml/*.xml'],
}