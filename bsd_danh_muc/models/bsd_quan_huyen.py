# -*- coding:utf-8 -*-

from odoo import models, fields, api


class BsdQuanHuyen(models.Model):
    _name = 'bsd.quan_huyen'
    _rec_name = 'bsd_ten'
    _description = 'Danh mục quận huyện'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    bsd_quoc_gia_id = fields.Many2one('res.country', string="Quốc gia", required=True, help="Tên quốc gia")
    bsd_tinh_thanh_id = fields.Many2one('res.country.state', string="Tỉnh thành", help="Tên tỉnh thành",
                                        required=True)
    bsd_ten = fields.Char(string="Tên quận huyện", required=True, help="Tên quận huyện")
    bsd_ma = fields.Char(string="Mã quận huyện", required=True, help="Mã quận huyện")
    _sql_constraints = [
        ('bsd_ma_unique', 'unique (bsd_ma)',
         'Mã quận huyện đã tồn tại !'),
    ]
    bsd_dien_giai = fields.Char(string="Diễn giải", help="Diễn giải")
    state = fields.Selection([('active', "Đang sử dụng"),
                              ('inactive', "Không sử dụng")], string='Trạng thái',
                             default='active', tracking=1, help="Trạng thái")
