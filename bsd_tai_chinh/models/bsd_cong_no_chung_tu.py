# -*- coding:utf-8 -*-

from odoo import models, fields, api


class BsdCongNo(models.Model):
    _name = 'bsd.cong_no_ct'
    _description = 'Công nợ chứng từ'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _rec_name = 'bsd_khach_hang_id'

    bsd_ngay_pb = fields.Date(string="Ngày", help="Ngày phân bổ")
    bsd_khach_hang_id = fields.Many2one('res.partner', string="Khách hàng", help="Khách hàng")
    bsd_ps_tang_id = fields.Many2one('bsd.cong_no', string="Phát sinh tăng", help="Chứng tù phát sinh tăng công nợ")
    bsd_ps_giam_id = fields.Many2one('bsd.cong_no', string="Phát sinh giảm", help="Chứng từ phát sinh giảm công nợ")
    bsd_tien_pb = fields.Monetary(string="Tiền", help="Tiền phân bổ")
    company_id = fields.Many2one('res.company', string='Công ty', default=lambda self: self.env.company)
    currency_id = fields.Many2one(related="company_id.currency_id", string="Tiền tệ", readonly=True)
    state = fields.Selection([('hoan_thanh', 'Hoàn thành'), ('huy', 'Hủy')])
