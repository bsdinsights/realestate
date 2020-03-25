# -*- coding:utf-8 -*-

from odoo import models, fields, api


class BsdGiuChoThienChi(models.Model):
    _name = 'bsd.gc_tc'
    _description = 'Giữ chỗ thiện chí'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _rec_name = 'bsd_ma_gctc'

    bsd_ma_gctc = fields.Char(string="Mã giữ chỗ", required=True, help="Mã giữ chỗ thiện chí")
    bsd_ngay_gctc = fields.Datetime(string="Ngày giữ chỗ", required=True, help="Ngày giữ chỗ thiện chí")
    bsd_khach_hang_id = fields.Many2one('res.partner', string="Khách hàng", required=True)
    bsd_du_an_id = fields.Many2one('bsd.du_an', string="Dự án", required=True)
    bsd_tien_gc = fields.Monetary(string="Tiền giữ chỗ", help="Tiền giữ chỗ thiện chí",
                                  related='bsd_du_an_id.bsd_tien_gc', store=True)
    bsd_dien_giai = fields.Char(string="Diễn giải")
    bsd_nvbh_id = fields.Many2one('res.users', string="Nhân viên BH", help="Nhân viên bán hàng")
    bsd_san_gd_id = fields.Many2one('res.partner', string="Sàn giao dịch", domain=[('is_company', '=', True)])
    bsd_ctv_id = fields.Many2one('res.partner', string="Cộng tác viên", domain=[('is_company', '=', False)])
    bsd_gioi_thieu_id = fields.Many2one('res.partner', string="Giới thiệu", help="Cá nhân hoặc đơn vị giới thiệu")
    bsd_hl_gc = fields.Datetime(string="Hạn giữ chỗ", help="Hiệu lực của giữ chỗ", required=True)
    bsd_ngay_tt = fields.Datetime(string="Ngày thanh toán", help="Ngày (kế toán xác nhận) thanh toán giữ chỗ")
    bsd_ngay_ut = fields.Datetime(string="Ưu tiên ráp căn",
                                  help="Thời gian được sử dụng để xét ưu tiên khi làm phiếu ráp căn")
    bsd_het_han = fields.Boolean(string="Hết hạn", help="Giữ chỗ bị hết hạn sau khi thanh toán đủ")
    bsd_ngay_rc = fields.Datetime(string="Ngày ráp căn", help="Ngày thực tế ráp căn", readonly=True)
    bsd_ngay_huy = fields.Datetime(string="Hủy ráp căn", help="Ngày hủy ráp căn", readonly=True)
    bsd_rap_can_id = fields.Many2one('bsd.rap_can', string="Ráp căn", help="Phiếu ráp căn")
    state = fields.Selection([('nhap', 'Nháp'),
                              ('giu_cho', 'Giữ chỗ'),
                              ('thanh_toan', 'Thanh toán'),
                              ('rap_can', 'Ráp căn'),
                              ('huy', 'Hủy')], string="Trạng thái", default="nhap")
    company_id = fields.Many2one('res.company', string='Công ty', default=lambda self: self.env.company)
    currency_id = fields.Many2one(related="company_id.currency_id", string="Tiền tệ", readonly=True)
