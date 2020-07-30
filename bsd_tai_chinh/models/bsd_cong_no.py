# -*- coding:utf-8 -*-

from odoo import models, fields, api


class BsdCongNo(models.Model):
    _name = 'bsd.cong_no'
    _description = 'Công nợ khách hàng'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _rec_name = 'bsd_chung_tu'

    bsd_chung_tu = fields.Char(string="Số chứng từ", readonly=True)
    bsd_ngay = fields.Date(string="Ngày", help="Ngày chứng từ")
    bsd_khach_hang_id = fields.Many2one('res.partner', string="Khách hàng", help="Khách hàng")
    bsd_du_an_id = fields.Many2one('bsd.du_an', string="Dự án", help="Tên dự án")
    bsd_ps_tang = fields.Monetary(string="Phát sinh tăng", help="Phát sinh tăng")
    bsd_ps_giam = fields.Monetary(string="Phát sinh giảm", help="Phát sinh giảm")
    bsd_tien = fields.Monetary(string="Tiền", help="Tiền phát sinh", compute="_compute_tien", store=True)
    bsd_loai_ct = fields.Selection([('gc_tc', 'Giữ chỗ thiện chí'), ('giu_cho', 'Giữ chỗ'),
                                    ('dat_coc', 'Đặt cọc'), ('dot_tt', 'Đợt thanh toán'),
                                    ('phieu_thu', 'Phiếu thu'),
                                    ('pql', 'Phí quản lý'),
                                    ('pbt', 'Phí bảo trì'),
                                    ('dc_giam', 'Điều chỉnh giảm'),
                                    ('dc_tang', 'Điều chỉnh tăng'),
                                    ('chuyen_tien', 'Chuyển tiền'),
                                    ('phi_ps', 'Phí phát sinh'),
                                    ('hoan_tien', 'Hoàn tiền')], string="Loại chứng từ", help="Loại chứng từ")
    bsd_phat_sinh = fields.Selection([('tang', 'Tăng'), ('giam', 'Giảm')], string="Phát sinh",
                                     help="Phát sinh tăng hoặc giảm công nợ")
    bsd_gc_tc_id = fields.Many2one('bsd.gc_tc', string="Giữ chỗ thiện chí", help="Giữ chỗ thiện chí")
    bsd_giu_cho_id = fields.Many2one('bsd.giu_cho', string="Giữ chỗ", help="Giữ chỗ")
    bsd_dat_coc_id = fields.Many2one('bsd.dat_coc', string="Đặt cọc", help="Đặt cọc")
    bsd_hd_ban_id = fields.Many2one('bsd.hd_ban', string="Hợp đồng", help="Hợp đồng")
    bsd_dot_tt_id = fields.Many2one('bsd.lich_thanh_toan', string="Đợt thanh toán")
    bsd_phieu_thu_id = fields.Many2one('bsd.phieu_thu', string="Phiếu thu", help="Phiếu thu")
    bsd_chuyen_tien_id = fields.Many2one('bsd.chuyen_tien', string="Chuyển tiền", help="Chuyển tiền")
    bsd_hoan_tien_id = fields.Many2one('bsd.hoan_tien', string="Hoàn tiền", help="Hoàn tiền")
    bsd_phi_ps_id = fields.Many2one('bsd.phi_ps', string="Phí phát sinh", help="Phí phát sinh")
    state = fields.Selection([('da_gs', 'Đã ghi sổ'), ('huy', 'Hủy')], string="Trạng thái", help="Trạng thái")
    company_id = fields.Many2one('res.company', string='Công ty', default=lambda self: self.env.company)
    currency_id = fields.Many2one(related="company_id.currency_id", string="Tiền tệ", readonly=True)

    bsd_giam_no_id = fields.Many2one('bsd.giam_no', string="Điều chỉnh giảm", help="Điều chỉnh giảm")
    bsd_tang_no_id = fields.Many2one('bsd.tang_no', string="Điều chỉnh tăng", help="Điều chỉnh tăng")

    @api.depends('bsd_ps_tang', 'bsd_ps_giam')
    def _compute_tien(self):
        for each in self:
            each.bsd_tien = each.bsd_ps_tang - each.bsd_ps_giam
