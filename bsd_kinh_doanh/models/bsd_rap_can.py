# -*- coding:utf-8 -*-

from odoo import models, fields, api
from odoo.exceptions import UserError
import datetime
import logging
_logger = logging.getLogger(__name__)


class BsdRapCan(models.Model):
    _name = 'bsd.rap_can'
    _description = "Thông tin ráp căn"
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _rec_name = 'bsd_ma_rc'

    bsd_ma_rc = fields.Char(string="Mã ráp căn", required=True,
                            readonly=True,
                            states={'nhap': [('readonly', False)]})
    _sql_constraints = [
        ('bsd_ma_rc_unique', 'unique (bsd_ma_rc)',
         'Mã ráp căn đã tồn tại !'),
    ]
    bsd_ngay_rc = fields.Datetime(string="Ngày ráp căn", required=True, default=fields.Datetime.now(),
                                  readonly=True,
                                  states={'nhap': [('readonly', False)]})
    bsd_gc_tc_id = fields.Many2one('bsd.gc_tc', string="Giữ chỗ thiện chí",
                                   help="Giữ chỗ trên dự án, chưa có sản phẩm", required=True,
                                        readonly=True,
                                        states={'nhap': [('readonly', False)]})
    bsd_khach_hang_id = fields.Many2one('res.partner', related="bsd_gc_tc_id.bsd_khach_hang_id", store=True)
    bsd_du_an_id = fields.Many2one('bsd.du_an', related="bsd_gc_tc_id.bsd_du_an_id", store=True)
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

    # KD.06.04 Ráp căn theo thời gian thanh toán giữ chỗ
    @api.constrains('bsd_gc_tc_id')
    def _constrain_gc_tc(self):
        if self.bsd_gc_tc_id:
            gc_tc = self.env['bsd.gc_tc'].search([('bsd_du_an_id', '=', self.bsd_du_an_id.id),
                                                  ('state', '=', 'thanh_toan'),
                                                  ('bsd_ngay_ut', '<', self.bsd_gc_tc_id.bsd_ngay_ut)])
            if gc_tc:
                raise UserError("Có Giữ chỗ thiện chí cần được Ráp căn trước .\n Vui lòng chờ đến lược của bạn!")

    # KD.06.01 xác nhận ráp căn
    def action_xac_nhan(self):
        self.write({
            'state': 'xac_nhan',
        })

    # KD.06.02 duyệt phiếu ráp căn
    def action_duyet(self):
        self.write({
            'state': 'duyet',
            'bsd_ngay_duyet': fields.Datetime.now(),
            'bsd_nguoi_duyet_id': self.env.uid,
        })
        self.bsd_gc_tc_id.write({
            'state': 'giu_cho',
            'bsd_rap_can_id': self.id,
            'bsd_ngay_rc': fields.Datetime.now(),
        })
        self.bsd_unit_id.write({
            'state': 'giu_cho',
        })
        # KD.06.05 Tự động tạo giữ chỗ khi ráp căn
        gc = self.env['bsd.giu_cho'].create({
                    'bsd_ma_gc': self.bsd_gc_tc_id.bsd_ma_gctc,
                    'bsd_ngay_gc': datetime.datetime.now(),
                    'bsd_khach_hang_id': self.bsd_gc_tc_id.bsd_khach_hang_id.id,
                    'bsd_du_an_id': self.bsd_gc_tc_id.bsd_du_an_id.id,
                    'bsd_unit_id': self.bsd_unit_id.id,
                    'bsd_tien_gc': self.bsd_gc_tc_id.bsd_tien_gc,
                    'bsd_nvbh_id': self.bsd_gc_tc_id.bsd_nvbh_id.id,
                    'bsd_san_gd_id': self.bsd_gc_tc_id.bsd_san_gd_id.id,
                    'bsd_gioi_thieu_id': self.bsd_gc_tc_id.bsd_gioi_thieu_id,
                    'bsd_gc_da': True,
                    'bsd_gc_tc_id': self.bsd_gc_tc_id.id,
                    'bsd_rap_can_id': self.id,
                    'state': 'giu_cho',
        })
        # cập nhật lại field giữ chỗ cho phiếu ráp căn
        self.write({
            'bsd_giu_cho_id': gc.id
        })

    # KD.06.03 Hủy phiếu ráp căn
    def action_huy(self):
        if self.bsd_giu_cho_id:
            if self.bsd_giu_cho_id.state != 'huy':
                raise UserError("Bạn cần hủy Giữ chỗ trước khi hủy ráp căn")
        else:
            pass
        self.write({
            'state': 'huy',
            'bsd_ngay_huy': fields.Datetime.now(),
            'bsd_nguoi_huy_id': self.env.uid,
        })
        self.bsd_gc_tc_id.write({
            'state': 'thanh_toan',
            'bsd_ngay_huy': fields.Datetime.now(),
        })
        self.bsd_unit_id.write({
            'state': 'chuan_bi',
        })

    # KD.06.06 Ràng buộc giữ chỗ thiện chí khi ráp căn
    @api.model
    def create(self,vals):
        rap_can = self.env['bsd.rap_can'].search([('bsd_gc_tc_id', '=', vals['bsd_gc_tc_id']),
                                                  ('state', '!=', 'huy')])
        _logger.debug(rap_can)
        if rap_can:
            raise UserError("Giữ chỗ thiện chí thuộc một ráp căn khác.\n Vui lòng kiểm tra lại.")
        res = super(BsdRapCan, self).create(vals)
        return res

