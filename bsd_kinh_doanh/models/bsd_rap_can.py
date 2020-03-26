# -*- coding:utf-8 -*-

from odoo import models, fields, api
from odoo.exceptions import UserError


class BsdRapCan(models.Model):
    _name = 'bsd.rap_can'
    _description = "Thông tin ráp căn"
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _rec_name = 'bsd_ma_rc'

    bsd_ma_rc = fields.Char(string="Mã ráp căn", required=True,
                                        readonly=True,
                                        states={'nhap': [('readonly', False)]})
    bsd_ngay_rc = fields.Datetime(string="Ngày ráp căn", required=True, default=fields.Datetime.now(),
                                        readonly=True,
                                        states={'nhap': [('readonly', False)]})
    bsd_gc_tc_id = fields.Many2one('bsd.gc_tc', string="Giữ chỗ thiện chí",
                                   help="Giữ chỗ trên dự án, chưa có sản phẩm", required=True,
                                        readonly=True,
                                        states={'nhap': [('readonly', False)]})
    bsd_khach_hang_id = fields.Many2one('res.partner', related="bsd_gc_tc_id.bsd_khach_hang_id")
    bsd_du_an_id = fields.Many2one('bsd.du_an', related="bsd_gc_tc_id.bsd_du_an_id")
    bsd_unit_id = fields.Many2one('product.product', string="Căn hộ", required=True,
                                        readonly=True,
                                        states={'nhap': [('readonly', False)]})
    bsd_dien_giai = fields.Char(string="Diễn giải",
                                        readonly=True,
                                        states={'nhap': [('readonly', False)]})
    bsd_ngay_duyet = fields.Datetime(string="Ngày duyệt")
    bsd_nguoi_duyet_id = fields.Many2one('res.users', string="Người duyệt")
    bsd_ngay_huy = fields.Datetime(string="Ngày hủy")
    bsd_nguoi_huy_id = fields.Many2one('res.users', string="Người hủy")
    bsd_giu_cho_id = fields.Many2one('bsd.giu_cho', string="Giữ chỗ")
    state = fields.Selection([('nhap', 'Nháp'),
                              ('xac_nhan', 'Xác nhận'),
                              ('duyet', 'Duyệt'),
                              ('huy', 'Hủy')], string="Trạng thái", default='nhap', tracking=1)

    @api.constrains('bsd_gc_tc_id')
    def _constrain_gc_tc(self):
        if self.bsd_gc_tc_id:
            gc_tc = self.env['bsd.gc_tc'].search([('bsd_du_an_id', '=', self.bsd_du_an_id.id),
                                                  ('state', '=', 'thanh_toan'),
                                                  ('bsd_ngay_ut', '<', self.bsd_gc_tc_id.bsd_ngay_ut)])
            if gc_tc:
                raise UserError("Có Giữ chỗ thiện chí cần được Ráp căn trước .\n Vui lòng chờ đến lược của bạn!")

    def action_xac_nhan(self):
        self.write({
            'state': 'xac_nhan',
        })

    def action_duyet(self):
        self.write({
            'state': 'duyet',
            'bsd_ngay_duyet': fields.Datetime.now(),
            'bsd_nguoi_duyet_id': self.env.uid,
        })
        self.bsd_gc_tc_id.write({
            'state': 'rap_can',
            'bsd_rap_can_id': self.id,
            'bsd_ngay_rc': fields.Datetime.now(),
        })
        self.bsd_unit_id.write({
            'state': 'san_sang',
        })

    def action_huy(self):
        pass
