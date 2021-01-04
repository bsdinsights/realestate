# -*- coding:utf-8 -*-

from odoo import models, fields, api, _

import logging
_logger = logging.getLogger(__name__)


class BsdWizardKhongDuyetXNDHS(models.TransientModel):
    _name = 'bsd.wizard.khong_duyet.xn_dhs'
    _description = 'Ghi nhận lý do từ chối'

    def _get_xn_dhs(self):
        xn_dhs = self.env['bsd.xn_dhs'].browse(self._context.get('active_ids', []))
        return xn_dhs

    bsd_xn_dhs_id = fields.Many2one('bsd.xn_dhs', string="XN.ĐHS", default=_get_xn_dhs, readonly=True)
    bsd_ly_do = fields.Char(string="Lý do", required=True)

    def action_xac_nhan(self):
        self.bsd_xn_dhs_id.write({
            'bsd_ly_do': self.bsd_ly_do,
            'state': 'nhap',
        })
        self.bsd_xn_dhs_id.message_post(body='Lý do không duyệt: ' + self.bsd_ly_do)
        for ct in self.bsd_xn_dhs_id.bsd_ct_ids.filtered(lambda c: c.state == 'xac_nhan'):
            ct.write({"state": "nhap"})
