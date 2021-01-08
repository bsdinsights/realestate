# -*- coding:utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError
import logging
_logger = logging.getLogger(__name__)


class BsdAssignKH(models.TransientModel):
    _name = 'bsd.wizard.assign_kh'
    _description = 'Assign khách hàng cho nhân viên kinh doanh khác'

    def _get_kh(self):
        khach_hang = self.env['res.partner'].browse(self._context.get('active_ids', []))
        return [(6, 0, khach_hang.ids)]

    bsd_khach_hang_ids = fields.Many2many('res.partner', string="DS khách hàng", readonly=True, default=_get_kh)
    bsd_nvkd_id = fields.Many2one('res.users', string="Nhân viên KD", required=True)

    def action_xac_nhan(self):
        self.bsd_khach_hang_ids.write({
            'user_id': self.bsd_nvkd_id.id
        })


class BsdShareKH(models.TransientModel):
    _name = 'bsd.wizard.share_kh'
    _description = 'Share khách hàng cho nhân viên kinh doanh khác'

    def _get_kh(self):
        khach_hang = self.env['res.partner'].browse(self._context.get('active_ids', []))
        return [(6, 0, khach_hang.ids)]

    bsd_khach_hang_ids = fields.Many2many('res.partner', string="DS khách hàng", readonly=True, default=_get_kh)
    bsd_nvkd_id = fields.Many2one('res.users', string="Nhân viên KD", required=True)

    def action_xac_nhan(self):
        for kh in self.bsd_khach_hang_ids:
            self.bsd_nvkd_id.write({
                'bsd_kh_ids': [(4, kh.id)]
            })
