# -*- coding:utf-8 -*-
{
    'name': 'BSD Báo cáo',
    'version': 'V0.1',
    'category': 'App',
    'author': 'Thịnh Lưu',
    'depends': [
        'bsd_du_an',
        'bsd_kinh_doanh',
        'bsd_dich_vu',
        'bsd_tai_chinh',
    ],
    'data': [
        'views/assets.xml',
        'views/bao_cao_views.xml',
    ],
    'qweb': ['static/xml/*.xml'],
}