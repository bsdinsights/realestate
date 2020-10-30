# -*- coding:utf-8 -*-

from odoo import models, fields, api, _

import logging
_logger = logging.getLogger(__name__)


class BsdTBNT(models.TransientModel):
    _name = 'bsd.wizard.tb_bg'
    _description = 'Ghi nhận ngày gửi thông báo bàn giao'

    def _get_tb_bg(self):
        tb_bg = self.env['bsd.tb_bg'].browse(self._context.get('active_ids', []))
        return tb_bg

    bsd_tb_bg_id = fields.Many2one('bsd.tb_bg', string="Thông báo bàn giao", default=_get_tb_bg, readonly=True)
    bsd_ngay = fields.Date(string="Ngày", required=True)

    def action_xac_nhan(self):
        if self.bsd_tb_bg_id:
            self.bsd_tb_bg_id.write({
                'bsd_ngay_gui': self.bsd_ngay,
            })

