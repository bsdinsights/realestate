# -*- coding:utf-8 -*-

from odoo import models, fields, api, _

import logging
_logger = logging.getLogger(__name__)


class BsdKyHDB(models.TransientModel):
    _name = 'bsd.wizard.ky_hdb'
    _description = 'Xác nhận ngày ký hợp đồng'

    def _get_hdb(self):
        hdb = self.env['bsd.hd_ban'].browse(self._context.get('active_ids', []))
        return hdb

    bsd_hd_ban_id = fields.Many2one('bsd.hd_ban', string="Hợp đồng bán", default=_get_hdb, readonly=True)
    bsd_ngay_ky_hdb = fields.Datetime(string="Ngày ký hợp đồng", required=True)

    def action_xac_nhan(self):
        # Cập nhật trạng thái hợp đồng
        self.bsd_hd_ban_id.write({
            'bsd_ngay_ky_hdb': self.bsd_ngay_ky_hdb,
            'state': 'da_ky'
        })
        # Cập nhật field hợp đồng trên unit , chuyển trạng thái đã bán
        self.bsd_hd_ban_id.bsd_unit_id.write({
            'bsd_hd_ban_id': self.bsd_hd_ban_id.id,
            'state': 'da_ban',
        })
        self.bsd_hd_ban_id.tao_cong_no_dot_tt()

