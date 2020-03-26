# -*- coding:utf-8 -*-

from odoo import models, fields, api


class BsdRapCan(models.Model):
    _name = 'bsd.rap_can'
    _description = "Thông tin ráp căn"
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _rec_name = 'bsd_ma_rc'

    bsd_ma_rc = fields.Char(string="Mã ráp căn", required=True)
    bsd_ngay_rc = fields.Datetime(string="Ngày ráp căn", required=True, default=fields.Datetime.now())
    bsd_gc_tc_id = fields.Many2one('bsd.gc_tc', string="Giữ chỗ thiện chí",
                                   help="Giữ chỗ trên dự án, chưa có sản phẩm", required=True)
    bsd_khach_hang_id = fields.Many2one('res.partner', related="bsd_gc_tc_id.bsd_khach_hang_id")
    bsd_du_an_id = fields.Many2one('bsd.du_an', related="bsd_gc_tc_id.bsd_du_an_id")
    bsd_unit_id = fields.Many2one('product.product', string="Căn hộ", required=True)
    bsd_dien_giai = fields.Char(string="Diễn giải")
    bsd_ngay_duyet = fields.Datetime(string="Ngày duyệt")
    bsd_nguoi_duyet_id = fields.Many2one('res.users', string="Người duyệt")
    bsd_ngay_huy = fields.Datetime(string="Ngày hủy")
    bsd_nguoi_huy_id = fields.Many2one('res.users', string="Người hủy")
    bsd_giu_cho_id = fields.Many2one('bsd.giu_cho', string="Giữ chỗ")
    state = fields.Selection([('nhap', 'Nháp'),
                              ('xac_nhan', 'Xác nhận'),
                              ('duyet', 'Duyệt'),
                              ('huy', 'Hủy')], string="Trạng thái", default='nhap')
