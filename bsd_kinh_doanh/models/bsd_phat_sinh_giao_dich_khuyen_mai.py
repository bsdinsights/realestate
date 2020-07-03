# -*- coding: utf-8 -*-

from odoo import models, fields, api
import logging
_logger = logging.getLogger(__name__)


class BsdPSGDKM(models.Model):
    _name = 'bsd.ps_gd_km'
    _description = 'Thông tin phát sinh giao dịch chiết khấu'
    _rec_name = 'bsd_ma_ht'

    bsd_ma_ht = fields.Char(string="Mã hệ thống", help="Mã hệ thống", required=True, readonly=True, copy=False,
                                   default='/')
    _sql_constraints = [
        ('bsd_ma_ht_unique', 'unique (bsd_ma_ht)',
         'Mã hệ thống đã tồn tại !'),
    ]
    bsd_khuyen_mai_id = fields.Char('bsd.khuyen_mai', string="Tên khuyến mãi", required=True, help="Tên khuyến mãi")
    bsd_ma_km = fields.Char(string="Mã khuyến mãi", required=True, help="Mã khuyến mãi")
    bsd_dot_mb_id = fields.Many2one('bsd.dot_mb', string="Đợt mở bán", help="Đợt mở bán ")
    bsd_hd_ban_id = fields.Many2one('bsd.hd_ban', string="Hợp đồng", help="Hợp đồng bán")
    bsd_khach_hang_id = fields.Many2one('res.partner', string="Khách hàng")
    bsd_gia_tri = fields.Monetary(string="Giá trị", help="Giá trị (tiền) khuyến mãi được hưởng")
    bsd_dien_giai = fields.Char(string="Diễn giải", help="Diễn giải")
    bsd_tu_ngay = fields.Date(string="Từ ngày", help="Từ ngày")
    bsd_den_ngay = fields.Date(string="Đến ngày", help="Đến ngày")
    bsd_tong_tt = fields.Monetary(string="Tổng thanh toán", help="Tổng giá trị thanh toán")
    bsd_tl_tt = fields.Float(string="Tỷ lệ thanh toán", help="Tổng tỷ lệ thanh toán")
    bsd_ngay_tt = fields.Date(string="Ngày thanh toán", help="Ngày tạo giao dịch khuyến mãi")
    company_id = fields.Many2one('res.company', string='Công ty', default=lambda self: self.env.company)
    currency_id = fields.Many2one(related="company_id.currency_id", string="Tiền tệ", readonly=True)
    state = fields.Selection([('nhap', 'Nháp'),
                              ('xac_nhan', 'Xác nhận'),
                              ('duyet', 'Duyệt'),
                              ('huy', 'Hủy')], string="Trạng thái",
                             default='xac_nhan', tracking=1, help="Trạng thái", required=True)