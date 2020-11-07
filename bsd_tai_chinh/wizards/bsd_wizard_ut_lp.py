# -*- coding:utf-8 -*-

from odoo import models, fields, api, _

import logging
_logger = logging.getLogger(__name__)


class BsdUoctinhLaiPhat(models.TransientModel):
    _name = 'bsd.wizard.uoc_tinh_lp'
    _description = 'Ước tính tiền phạt chậm thanh toán'

    def _get_hdb(self):
        hdb = self.env['bsd.hd_ban'].browse(self._context.get('active_ids', []))
        return hdb

    bsd_hd_ban_id = fields.Many2one('bsd.hd_ban', string="Hợp đồng bán", default=_get_hdb, readonly=True)
    bsd_ngay_ut = fields.Date(string="Ngày ước tính", required=True)
    company_id = fields.Many2one('res.company', string='Công ty', default=lambda self: self.env.company)
    currency_id = fields.Many2one(related="company_id.currency_id", string="Tiền tệ", readonly=True)

    def action_in(self):
        data = {
            'ids': self.bsd_hd_ban_id.ids,
            'model': self.bsd_hd_ban_id._name,
            'bsd_ngay_ut': self.bsd_ngay_ut,
        }
        ref_id = 'bsd_tai_chinh.bsd_mau_in_uoc_tinh_lp'
        return self.env.ref(ref_id).report_action(self, data=data)