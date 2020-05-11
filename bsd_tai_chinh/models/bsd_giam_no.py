# -*- coding:utf-8 -*-

from odoo import models, fields, api


class BsdGiamNo(models.Model):
    _name = 'bsd.giam_no'
    _description = 'Phiếu ghi giảm nợ khách hàng'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _rec_name = 'bsd_so_ct'

    bsd_so_ct = fields.Char(string="Số", help="Số chứng từ", required=True)
    _sql_constraints = [
        ('bsd_so_ct_unique', 'unique (bsd_so_ct)',
         'Số chứng từ giảm nợ đã tồn tại !'),
    ]
    bsd_ngay_ct = fields.Datetime(string="Ngày", help="Ngày chứng từ", required=True,
                                  default=lambda self: fields.Datetime.now())
    bsd_loai_dc = fields.Selection([('khac', 'Điều chỉnh khác')], string="Loại điều chỉnh", help="Loại điều chỉnh")
    bsd_dien_giai = fields.Char(string="Diễn giải", help="Lý do điều chỉnh")
    bsd_khach_hang_id = fields.Many2one('res.partner', string="Khách hàng", help="Khách hàng", required=True)
    bsd_du_an_id = fields.Many2one('bsd.du_an', string="Dự án", help="Dự án", required=True)
    bsd_unit_id = fields.Many2one('product.product', string="Căn hộ", help="Căn hộ")
    bsd_tien = fields.Monetary(string="Tiền", help="Tiền điều chỉnh", required=True)
    state = fields.Selection([('nhap', 'Nháp'), ('xac_nhan', 'Xác nhận'),
                              ('da_gs', 'Đã ghi sổ'), ('huy', 'Hủy')], string="Trạng thái", tracking=1,
                             required=True, default='nhap')
    company_id = fields.Many2one('res.company', string='Công ty', default=lambda self: self.env.company)
    currency_id = fields.Many2one(related="company_id.currency_id", string="Tiền tệ", readonly=True)