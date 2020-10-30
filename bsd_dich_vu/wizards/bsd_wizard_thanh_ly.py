# -*- coding:utf-8 -*-

from odoo import models, fields, api, _

import logging
_logger = logging.getLogger(__name__)


class BsdKyThanhLy(models.TransientModel):
    _name = 'bsd.wizard.ky_thanh_ly'
    _description = 'Xác nhận ngày ký biên bản thanh lý'

    def _get_thanh_ly(self):
        thanh_ly = self.env['bsd.hd_ban'].browse(self._context.get('active_ids', []))
        return thanh_ly

    bsd_thanh_ly_id = fields.Many2one('bsd.thanh_ly', string="Biên bản thanh lý", default=_get_thanh_ly, readonly=True)
    bsd_ngay_ky_thanh_ly = fields.Date(string="Ngày ký ", required=True)

    def action_xac_nhan(self):
        self.bsd_thanh_ly_id.write({
            'bsd_ngay_ky': self.bsd_ngay_ky_thanh_ly,
            'state': 'da_ky'
        })
        
        
# -*- coding:utf-8 -*-

from odoo import models, fields, api, _

import logging
_logger = logging.getLogger(__name__)


class BsdHuyThanhLy(models.TransientModel):
    _name = 'bsd.wizard.huy_tl'
    _description = 'Ghi nhận lý do hủy thanh lý'

    def _get_thanh_ly(self):
        thanh_ly = self.env['bsd.thanh_ly'].browse(self._context.get('active_ids', []))
        return thanh_ly

    bsd_thanh_ly_id = fields.Many2one('bsd.thanh_ly', string="Thanh lý", default=_get_thanh_ly, readonly=True)
    bsd_ly_do = fields.Char(string="Lý do", required=True)

    def action_xac_nhan(self):
        self.bsd_thanh_ly_id.write({
            'bsd_ly_do': self.bsd_ly_do,
            'state': 'huy',
        })