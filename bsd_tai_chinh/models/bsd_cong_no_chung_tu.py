# -*- coding:utf-8 -*-

from odoo import models, fields, api


class BsdCongNo(models.Model):
    _name = 'bsd.cong_no_ct'
    _description = 'Công nợ chứng từ'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _rec_name = 'bsd_khach_hang_id'

    bsd_ngay_pb = fields.Date(string="Ngày", help="Ngày phân bổ")
    bsd_khach_hang_id = fields.Many2one('res.partner', string="Khách hàng", help="Khách hàng")
    bsd_tien_pb = fields.Monetary(string="Tiền", help="Tiền phân bổ")

    bsd_gc_tc_id = fields.Many2one('bsd.gc_tc', string="Giữ chỗ thiện chí", help="Giữ chỗ thiện chí")
    bsd_giu_cho_id = fields.Many2one('bsd.giu_cho', string="Giữ chỗ", help="Giữ chỗ")
    bsd_dat_coc_id = fields.Many2one('bsd.dat_coc', string="Đặt cọc", help="Đặt cọc")
    bsd_hd_ban_id = fields.Many2one('bsd.hd_ban', string="Hợp đồng", help="Hợp đồng")
    bsd_dot_tt_id = fields.Many2one('bsd.lich_thanh_toan', string="Đợt thanh toán")
    bsd_phieu_thu_id = fields.Many2one('bsd.phieu_thu', string="Phiếu thu", help="Phiếu thu")

    company_id = fields.Many2one('res.company', string='Công ty', default=lambda self: self.env.company)
    currency_id = fields.Many2one(related="company_id.currency_id", string="Tiền tệ", readonly=True)
    state = fields.Selection([('hoan_thanh', 'Hoàn thành'), ('huy', 'Hủy')])
