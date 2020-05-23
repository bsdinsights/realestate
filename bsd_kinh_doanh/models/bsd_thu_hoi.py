# -*- coding:utf-8 -*-

from odoo import models, fields, api
from odoo.exceptions import UserError
import datetime
import logging
_logger = logging.getLogger(__name__)


class BsdThuHoi(models.Model):
    _name = 'bsd.thu_hoi'
    _description = 'Thu hồi căn hộ trong đợt phát hành'
    _rec_name = 'bsd_ma_th'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    bsd_ma_th = fields.Char(string="Mã", help="Mã đợt thu hồi căn hộ", required=True,
                            readonly=True,
                            states={'nhap': [('readonly', False)]})
    bsd_ngay_th = fields.Date(string="Ngày", help="Ngày trên phiếu thu hồi căn hộ", required=True,
                              readonly=True, default = lambda self: fields.Date.today(),
                              states={'nhap': [('readonly', False)]})
    bsd_ly_do = fields.Char(string="Lý do thu hồi", help="Lý do thu hồi", required=True,
                            readonly=True,
                            states={'nhap': [('readonly', False)]})
    bsd_du_an_id = fields.Many2one('bsd.du_an', string="Dự án", help="Dự án", required=True,
                                   readonly=True,
                                   states={'nhap': [('readonly', False)]})
    bsd_dot_mb_id = fields.Many2one('bsd.dot_mb', string="Đợt mở bán", help="Đợt mở bán", required=True,
                                    readonly=True,
                                    states={'nhap': [('readonly', False)]})
    bsd_ngay_duyet = fields.Datetime(string="Ngày duyệt", help="Người duyệt thu hồi đợt mở bán", readonly=True)
    bsd_nguoi_duyet = fields.Many2one('res.users', string="Người duyệt", help="Người duyệt thu hồi đợt mở bán",
                                      readonly=True)
    bsd_ly_do_khong_duyet = fields.Char(string="Lý do", readonly=True, tracking=2)
    state = fields.Selection([('nhap', 'Nháp'), ('xac_nhan', 'Xác nhận'),
                              ('duyet', 'Duyệt'), ('huy', 'Hủy')], string="Trạng thái", help="Trạng thái",
                             tracking=1, required=True, default='nhap')
    bsd_unit_ids = fields.Many2many('product.product', string="Danh sách căn hộ",
                                    readonly=True,
                                    states={'nhap': [('readonly', False)]})

    # KD.04.04.03 - Xác nhận thu hồi căn hộ đợt mở bán
    def action_xac_nhan(self):
        if not self.bsd_unit_ids:
            raise UserError("Chưa có căn hộ thu hồi. Vui lòng kiểm tra lại!")
        if self.bsd_dot_mb_id.state != 'ph' or self.bsd_dot_mb_id.bsd_den_ngay < datetime.date.today():
            raise UserError("Vui lòng kiểm tra lại thông tin đợt mở bán")
        self.write({
            'state': 'xac_nhan',
        })

    # KD.04.04.04 - Duyệt thu hồi căn hộ
    def action_duyet(self):
        if self.bsd_dot_mb_id.state != 'ph' or self.bsd_dot_mb_id.bsd_den_ngay < datetime.date.today():
            raise UserError("Vui lòng kiểm tra lại thông tin đợt mở bán")
        # cập nhật thông tin phiếu thu hồi
        self.write({
            'state': 'duyet',
            'bsd_ngay_duyet': datetime.datetime.now(),
            'bsd_nguoi_duyet': self.env.uid
        })
        # cập nhật căn hộ được thu hồi
        self.bsd_unit_ids.write({
            'state': 'chuan_bi',
            'bsd_dot_mb_id': False,
        })
        # cập nhật căn hộ phát hành
        ph = self.bsd_dot_mb_id.bsd_ph_ids.filtered(lambda p: p.bsd_unit_id.id in self.bsd_unit_ids.ids)
        _logger.debug("phát hành")
        _logger.debug(ph)
        ph.write({
            'state': 'thu_hoi',
            'bsd_thu_hoi_id': self.id,
        })

    # KD.04.04.05 - Không duyệt thu hồi căn hộ
    def action_khong_duyet(self):
        action = self.env.ref('bsd_kinh_doanh.bsd_wizard_thu_hoi_action').read()[0]
        return action

    # KD.04.04.06 - Hủy thu hồi căn hộ
    def action_huy(self):
        self.write({
            'state': 'huy',
        })






