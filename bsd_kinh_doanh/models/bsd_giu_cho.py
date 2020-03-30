# -*- coding:utf-8 -*-

from odoo import models, fields, api
import datetime


class BsdRapCan(models.Model):
    _name = 'bsd.giu_cho'
    _description = "Thông tin giữ chỗ"
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _rec_name = 'bsd_ma_gc'

    bsd_ma_gc = fields.Char(string="Mã giữ chỗ", required=True,
                              readonly=True,
                              states={'nhap': [('readonly', False)]})
    bsd_ngay_gc = fields.Datetime(string="Ngày giữ chỗ", required=True, default=datetime.datetime.now(),
                              readonly=True,
                              states={'nhap': [('readonly', False)]})
    bsd_khach_hang_id = fields.Many2one('res.partner', string="Khách hàng", required=True,
                              readonly=True,
                              states={'nhap': [('readonly', False)]})
    bsd_du_an_id = fields.Many2one('bsd.du_an', string="Dự án", required=True,
                              readonly=True,
                              states={'nhap': [('readonly', False)]})
    bsd_unit_id = fields.Many2one('product.product', string="Căn hộ", required=True,
                              readonly=True,
                              states={'nhap': [('readonly', False)]})
    bsd_dien_giai = fields.Char(string="Diễn giải",
                              readonly=True,
                              states={'nhap': [('readonly', False)]})
    bsd_dot_mb_id = fields.Many2one('bsd.dot_mb', related="bsd_unit_id.bsd_dot_mb_id",string="Đợt mở bán", store=True)
    bsd_bang_gia_id = fields.Many2one('product.pricelist', related="bsd_dot_mb_id.bsd_bang_gia_id", store=True,
                                      string="Bảng giá")
    bsd_tien_gc = fields.Monetary(string="Tiền giữ chỗ", required=True,
                              readonly=True,
                              states={'nhap': [('readonly', False)]})
    bsd_nvbh_id = fields.Many2one('res.users', string="Nhân viên BH",
                              readonly=True,
                              states={'nhap': [('readonly', False)]})
    bsd_san_gd_id = fields.Many2one('res.partner', string="Sàn giao dịch",domain=[('is_company', '=', True)],
                              readonly=True,
                              states={'nhap': [('readonly', False)]})
    bsd_ctv_id = fields.Many2one('res.partner', string="Công tác viên",domain=[('is_company', '=', False)],
                              readonly=True,
                              states={'nhap': [('readonly', False)]})
    bsd_gioi_thieu_id = fields.Many2one('res.partner', string="Giới thiệu",help="Cá nhân hoặc đơn vị giới thiệu",
                              readonly=True,
                              states={'nhap': [('readonly', False)]})
    bsd_hl_gc = fields.Datetime(string="Hạn giữ chỗ", help="Hiệu lực của giữ chỗ", compute='_compute_hl_gc', store=True)
    bsd_gc_da = fields.Boolean(string="Giữ chỗ dự án", help="""Thông tin ghi nhận Giữ chỗ được tự động tạo từ 
                                                                giữ chỗ thiện chí hay không""", readonly=True)
    bsd_gc_tc_id = fields.Many2one('bsd.gc_tc', string="Giữ chỗ thiện chí", readonly=True)
    bsd_rap_can_id = fields.Many2one('bsd.rap_can', string="Ráp căn", help="Phiếu ráp căn", readonly=True)
    state = fields.Selection([('nhap', 'Nháp'),
                              ('dat_cho', 'Đặt chỗ'),
                              ('giu_cho', 'Giữ chỗ'),
                              ('bao_gia', 'Báo giá'),
                              ('huy', 'Hủy')], default='nhap', string="Trạng thái", tracking=1)
    company_id = fields.Many2one('res.company', string='Công ty', default=lambda self: self.env.company)
    currency_id = fields.Many2one(related="company_id.currency_id", string="Tiền tệ", readonly=True)

    @api.onchange('bsd_unit_id', 'bsd_du_an_id')
    def _onchange_tien_gc(self):
        if self.bsd_unit_id:
            tien_gc = self.bsd_unit_id.bsd_tien_gc
            if tien_gc != 0:
                self.bsd_tien_gc = tien_gc
            else:
                self.bsd.tien_gc = self.bsd_du_an_id.bsd_tien_gc

    # R.05 Tính hạn hiệu lực giữ chỗ
    @api.depends('bsd_ngay_gc', 'bsd_du_an_id')
    def _compute_hl_gc(self):
        if self.bsd_ngay_gc:
            if not self.bsd_dot_mb_id:
                days = self.bsd_du_an_id.bsd_gc_tmb or 0 if self.bsd_du_an_id else 0
                self.bsd_hl_gc = self.bsd_ngay_gc + datetime.timedelta(days=days)
            else:
                hours = self.bsd_du_an_id.bsd_gc_smb or 0 if self.bsd_du_an_id else 0
                self.bsd_hl_gc = self.bsd_ngay_gc + datetime.timedelta(hours=hours)

    # KD07.01 Xác nhận giữ chỗ
    def action_xac_nhan(self):
        if not self.bsd_dot_mb_id:
            self.write({
                'state': 'dat_cho',
                'bsd_ngay_gc': datetime.datetime.now(),
            })
            # Cập nhật lại trạng thái unit
            self.bsd_unit_id.write({
                'state': 'dat_cho',
            })
        else:
            self.write({
                'state': 'giu_cho',
                'bsd_ngay_gc': datetime.datetime.now(),
            })
            # Cập nhật lại trạng thái unit
            self.bsd_unit_id.write({
                'state': 'giu_cho',
            })
