# -*- coding:utf-8 -*-

from odoo import models, fields, api, _

import logging
_logger = logging.getLogger(__name__)


class BsdWizardPhiPS(models.TransientModel):
    _name = 'bsd.wizard.phi_mg'
    _description = 'Ghi nhận lý do từ chối'

    def _get_phi_mg(self):
        phi_mg = self.env['bsd.phi_mg'].browse(self._context.get('active_ids', []))
        return phi_mg

    bsd_phi_mg_id = fields.Many2one('bsd.phi_mg', string="Hoa hồng", default=_get_phi_mg, readonly=True)
    bsd_ly_do = fields.Char(string="Lý do", required=True)

    def action_xac_nhan(self):
        self.bsd_phi_mg_id.write({
            'bsd_ly_do': self.bsd_ly_do,
            'state': 'nhap',
        })
        self.bsd_phi_mg_id.message_post(body='Lý do không duyệt: ' + self.bsd_ly_do)
