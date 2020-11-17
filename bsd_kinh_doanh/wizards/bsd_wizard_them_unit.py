# -*- coding:utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError
import logging
_logger = logging.getLogger(__name__)


class BsdKyBG(models.TransientModel):
    _name = 'bsd.wizard.them_unit'
    _description = 'Ghi nhận lý do từ chối'

    def _get_them_unit(self):
        them_unit = self.env['bsd.them_unit'].browse(self._context.get('active_ids', []))
        return them_unit

    bsd_them_unit_id = fields.Many2one('bsd.them_unit', string="Thêm unit", default=_get_them_unit, readonly=True)
    bsd_ly_do = fields.Char(string="Lý do", required=True)

    def action_xac_nhan(self):
        self.bsd_them_unit_id.write({
            'bsd_ly_do': self.bsd_ly_do,
            'state': 'nhap',
        })


class BsdPhatHanhThemUnit(models.TransientModel):
    _name = 'bsd.wizard.ph_them_unit'
    _description = 'Phát hành thêm sản phẩm'

    def _get_them_sp(self):
        them_sp = self.env['bsd.them_unit'].browse(self._context.get('active_ids', []))
        return them_sp

    bsd_them_unit_id = fields.Many2one('bsd.them_unit', string="Thêm SP", default=_get_them_sp, readonly=True)
    bsd_so_gio = fields.Integer(string="Thời gian gia hạn GC (giờ)", required=True)

    @api.constrains('bsd_so_gio')
    def _constrains_so_gio(self):
        if self.bsd_so_gio <= 0:
            raise UserError(_("Số giờ gia hạn giữ chỗ không được nhỏ hơn hoặc bằng không.\n"
                              "Vui lòng kiểm tra thông tin."))

    def action_xac_nhan(self):
        self.bsd_them_unit_id.action_phat_hanh_wizard(self.bsd_so_gio)

