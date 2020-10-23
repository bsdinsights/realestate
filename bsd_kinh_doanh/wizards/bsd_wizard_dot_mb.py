# -*- coding:utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError
import logging
_logger = logging.getLogger(__name__)


class BsdPhatHanhDMB(models.TransientModel):
    _name = 'bsd.wizard.ph_dot_mb'
    _description = 'Phát hành đợt mở bán'

    def _get_dot_mb(self):
        dot_mb = self.env['bsd.dot_mb'].browse(self._context.get('active_ids', []))
        return dot_mb

    bsd_dot_mb_id = fields.Many2one('bsd.dot_mb', string="Đợt mở bán", default=_get_dot_mb, readonly=True)
    bsd_so_gio = fields.Integer(string="Thời gian gia hạn GC (giờ)", required=True)

    @api.constrains('bsd_so_gio')
    def _constrains_so_gio(self):
        if self.bsd_so_gio <= 0:
            raise UserError(_("Số giờ gia hạn giữ chỗ không được nhỏ hơn hoặc bằng không.\n"
                              "Vui lòng kiểm tra thông tin."))

    def action_xac_nhan(self):
        self.bsd_dot_mb_id.action_phat_hanh_wizard(self.bsd_so_gio)
