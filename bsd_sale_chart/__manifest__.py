# -*- coding:utf-8 -*-
{
    'name': 'BSD Sale Chart',
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
    ],
    'qweb': ['static/xml/*.xml'],
}