# -*- coding:utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError
import datetime
import logging
_logger = logging.getLogger(__name__)


class BsdThuHoi(models.Model):
    _name = 'bsd.thu_hoi'
    _description = 'Thu hồi Sản phẩm trong đợt phát hành'
    _rec_name = 'bsd_ma_th'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    bsd_ma_th = fields.Char(string="Mã", required=True, readonly=True, copy=False, default='/')
    _sql_constraints = [
        ('bsd_ma_th_unique', 'unique (bsd_ma_th)',
         'Mã thu hồi đã tồn tại !'),
    ]
    bsd_ngay_th = fields.Date(string="Ngày", help="Ngày trên phiếu thu hồi Sản phẩm", required=True,
                              readonly=True, default=lambda self: fields.Date.today(),
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
    bsd_unit_ids = fields.Many2many('product.product', string="Danh sách Sản phẩm",
                                    readonly=True,
                                    states={'nhap': [('readonly', False)]})

    # KD.04.04.03 - Xác nhận thu hồi Sản phẩm đợt mở bán
    def action_xac_nhan(self):
        if not self.bsd_unit_ids:
            raise UserError("Chưa có Sản phẩm thu hồi. Vui lòng kiểm tra lại!")
        if self.bsd_dot_mb_id.state != 'ph' or self.bsd_dot_mb_id.bsd_den_ngay < datetime.date.today():
            raise UserError("Vui lòng kiểm tra lại thông tin đợt mở bán")
        self.write({
            'state': 'xac_nhan',
        })

    # KD.04.04.04 - Duyệt thu hồi Sản phẩm
    def action_duyet(self):
        if self.bsd_dot_mb_id.state != 'ph' or self.bsd_dot_mb_id.bsd_den_ngay < datetime.date.today():
            raise UserError("Vui lòng kiểm tra lại thông tin đợt mở bán")
        # cập nhật thông tin phiếu thu hồi
        self.write({
            'state': 'duyet',
            'bsd_ngay_duyet': datetime.datetime.now(),
            'bsd_nguoi_duyet': self.env.uid
        })
        # cập nhật Sản phẩm được thu hồi
        self.bsd_unit_ids.write({
            'state': 'chuan_bi',
            'bsd_dot_mb_id': False,
        })
        # cập nhật Sản phẩm phát hành
        ph = self.bsd_dot_mb_id.bsd_ph_ids.filtered(lambda p: p.bsd_unit_id.id in self.bsd_unit_ids.ids)
        _logger.debug("phát hành")
        _logger.debug(ph)
        ph.write({
            'state': 'thu_hoi',
            'bsd_thu_hoi_id': self.id,
        })

    # KD.04.04.05 - Không duyệt thu hồi Sản phẩm
    def action_khong_duyet(self):
        action = self.env.ref('bsd_kinh_doanh.bsd_wizard_thu_hoi_action').read()[0]
        return action

    # KD.04.04.06 - Hủy thu hồi Sản phẩm
    def action_huy(self):
        self.write({
            'state': 'huy',
        })

    @api.model
    def create(self, vals):
        if 'bsd_du_an_id' in vals:
            du_an = self.env['bsd.du_an'].browse(vals['bsd_du_an_id'])
            sequence = du_an.get_ma_bo_cn(loai_cn=self._name)
        if not sequence:
            raise UserError(_('Dự án chưa có mã phiếu thu hồi Sản phẩm đợt mở bán'))
        vals['bsd_ma_th'] = sequence.next_by_id()
        res = super(BsdThuHoi, self).create(vals)
        return res





