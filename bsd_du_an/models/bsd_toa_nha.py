# -*- coding: utf-8 -*-

from odoo import models, fields, api


class BsdBlock(models.Model):
    _name = "bsd.toa_nha"
    _rec_name = 'bsd_ma_ht'
    _description = 'Thông tin tòa nhà'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    bsd_ten_tn = fields.Char(string="Tên tòa nhà", required=True, help="Tên tòa nhà")
    bsd_ma_tn = fields.Char(string="Mã tòa nhà", required=True, help="Mã tòa nhà")

    bsd_ma_ht = fields.Char(string="Mã hệ thống", help="Mã hệ thống dùng để nhập", compute="_compute_ma_ht", store=True)
    _sql_constraints = [
        ('bsd_ma_ht_unique', 'unique (bsd_ma_ht)',
         'Mã hệ thống đã tồn tại !'),
    ]

    @api.depends('bsd_ma_tn', 'bsd_du_an_id.bsd_ma_da')
    def _compute_ma_ht(self):
        for each in self:
            if self.bsd_ma_tn and self.bsd_du_an_id:
                ma_da = each.bsd_du_an_id.bsd_ma_da or ''
                each.bsd_ma_ht = ma_da + '-' + each.bsd_ma_tn

    bsd_stt = fields.Integer(string="Số thứ tự", help="Số thứ tự sắp xếp của tòa nhà")
    bsd_du_an_id = fields.Many2one('bsd.du_an', string="Dự án", required=True)
    bsd_so_tang = fields.Integer(string="Số tầng", help="Số tầng")
    bsd_so_unit = fields.Integer(string="Số căn hộ", help="Số căn hộ")
    bsd_dia_chi = fields.Text(string="Địa chỉ", help="Địa chỉ tòa nhà")
    state = fields.Selection([('active', 'Đang sử dụng'),
                              ('inactive', 'Ngưng sử dụng')],
                             string="Trạng thái", default='active', tracking=1, help="Trạng thái")
