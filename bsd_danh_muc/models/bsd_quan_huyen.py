# -*- coding:utf-8 -*-

from odoo import models, fields, api


class BsdQuanHuyen(models.Model):
    _name = 'bsd.quan_huyen'
    _rec_name = 'bsd_ten'
    _description = 'Danh mục quận huyện'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    bsd_quoc_gia_id = fields.Many2one('res.country', string="Quốc gia", required=True)
    bsd_tinh_thanh_id = fields.Many2one('res.country.state', string="Tỉnh thành",
                                        required=True)
    bsd_ten = fields.Char(string="Tên quận huyện", required=True)
    bsd_ma = fields.Char(string="Mã quận huyện", required=True, copy=False)
    bsd_dien_giai = fields.Char(string="Diễn giải")
    state = fields.Selection([('active', "Đang sử dụng"),
                                       ('inactive', "Không sử dụng")], string='Trạng thái', default='active')
    _sql_constraints = [
        ('bsd_ma_unique', 'unique(bsd_ma)', 'Mã đã được sử dung')
    ]
