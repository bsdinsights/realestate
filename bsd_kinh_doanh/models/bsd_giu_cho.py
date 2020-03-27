# -*- coding:utf-8 -*-

from odoo import models, fields, api


class BsdRapCan(models.Model):
    _name = 'bsd.giu_cho'
    _description = "Thông tin giữ chỗ"
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _rec_name = 'bsd_ma_gc'

    bsd_ma_gc = fields.Char(string="Mã giữ chỗ", required=True)
    bsd_ngay_gc = fields.Datetime(string="Ngày giữ chỗ", required=True)
    bsd_khach_hang_id = fields.Many2one('res.partner', string="Khách hàng", required=True)
    bsd_du_an_id = fields.Many2one('bsd.du_an', string="Dự án", required=True)
    bsd_unit_id = fields.Many2one('product.product', string="Căn hộ", required=True)
    bsd_dien_giai = fields.Char(string="Diễn giải")
    bsd_dot_mb_id = fields.Many2one('bsd.dot_mb_id', string="Đợt mở bán")
    bsd_bang_gia_id = fields.Many2one('product.pricelist', string="Bảng giá")
    bsd_tien_gc = fields.Monetary(string="Tiền giữ chỗ")
    bsd_nvbh_id = fields.Many2one('res.users', string="Nhân viên BH")
    bsd_san_gd_id = fields.Many2one('res.partner', string="Sàn giao dịch",
                                    domain=[('is_company', '=', True)])
    bsd_ctv_id = fields.Many2one('res.partner', string="Công tác viên",
                                 domain=[('is_company', '=', False)])
    bsd_gioi_thieu_id = fields.Many2one('res.partner', string="Giới thiệu",
                                        help="Cá nhân hoặc đơn vị giới thiệu")
    bsd_hl_gc = fields.Datetime(string="Hạn giữ chỗ", help="Hiệu lực của giữ chỗ")
    bsd_gc_da = fields.Boolean(string="Giữ chỗ dự án", help="""Thông tin ghi nhận Giữ chỗ được tự động tạo từ 
                                                                giữ chỗ thiện chí hay không""", readonly=True)
    bsd_gc_tc_id = fields.Many2one('bsd.gc_tc', string="Giữ chỗ thiện chí", readonly=True)
    bsd_rap_can_id = fields.Many2one('bsd.rap_can', string="Ráp căn", help="Phiếu ráp căn", readonly=True)
    state = fields.Selection([('nhap', 'Nháp'),
                              ('giu_cho', 'Giữ chỗ'),
                              ('thanh_toan', 'Thanh toán'),
                              ('bao_gia', 'Báo giá'),
                              ('huy', 'Hủy')], default='nhap', string="Trạng thái", tracking=1)
    company_id = fields.Many2one('res.company', string='Công ty', default=lambda self: self.env.company)
    currency_id = fields.Many2one(related="company_id.currency_id", string="Tiền tệ", readonly=True)
