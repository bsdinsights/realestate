# -*- coding:utf-8 -*-

from odoo import models, fields, api, _

import logging
_logger = logging.getLogger(__name__)


class BsdKyPLDSH(models.TransientModel):
    _name = 'bsd.wizard.ky_pl_dsh'
    _description = 'Xác nhận ngày ký phụ lục đồng sở hữu'

    def _get_pl_dsh(self):
        dsh = self.env['bsd.pl_dsh'].browse(self._context.get('active_ids', []))
        return dsh

    bsd_pl_dsh_id = fields.Many2one('bsd.pl_dsh', string="Phụ lục HĐ", default=_get_pl_dsh, readonly=True)
    bsd_ngay_ky_pl = fields.Datetime(string="Ngày ký phụ lục", required=True)

    def action_xac_nhan(self):
        self.bsd_pl_dsh_id.write({
            'bsd_ngay_ky_pl': self.bsd_ngay_ky_pl,
            'state': 'dk_pl'
        })
        self.bsd_pl_dsh_id.update_dsh()