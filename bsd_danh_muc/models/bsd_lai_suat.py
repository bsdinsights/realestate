# -*- coding:utf-8 -*-

from odoo import models, fields, api


class BsdLaiSuat(models.Model):
    _name = 'bsd.lai_suat'
    _description = "Bảng thông tin lại suất"
    _rec_name = 'bsd_ten'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    bsd_ma = fields.Char(string="Mã lãi suất", help="Mã lãi suất", required=True)
    _sql_constraints = [
        ('bsd_ma_unique', 'unique (bsd_ma)',
         'Mã lãi suất đã tồn tại !'),
    ]
    bsd_ten = fields.Char(string="Tên lãi suất", help="Tên lãi suất", required=True)
    bsd_du_an_id = fields.Many2one('bsd.du_an', string="Dự án", required=True, help="Tên dự án")
    bsd_ngay_ap_dung = fields.Date(string="Ngày áp dụng", required=True, help="Ngày áp dụng")
    bsd_lai_suat = fields.Float(string="Lãi suất", required=True, help="Lãi suất")
    bsd_dien_giai = fields.Char(string="Diễn giải", help="Diễn giải")
    state = fields.Selection([('active', 'Đang sử dụng'),
                              ('inactive', 'Ngưng sử dụng')],
                             string="Trạng thái", default='active', required=True, tracking=1, help="Trạng thái")