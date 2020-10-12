# -*- coding:utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError
import logging
_logger = logging.getLogger(__name__)


class BsdKyBG(models.TransientModel):
    _name = 'bsd.wizard.ky_bg'
    _description = 'Xác nhận ngày ký báo giá'

    def _get_bg(self):
        bg = self.env['bsd.bao_gia'].browse(self._context.get('active_ids', []))
        return bg

    bsd_bao_gia_id = fields.Many2one('bsd.bao_gia', string="Báo giá", default=_get_bg, readonly=True)
    bsd_ngay_ky_bg = fields.Datetime(string="Ngày ký báo giá", required=True)

    def action_xac_nhan(self):
        # Kiểm tra trạng thái unit trước khi ký bảng tính giá
        if self.bsd_bao_gia_id.bsd_unit_id.state not in ['giu_cho', 'san_sang']:
            raise UserError(_("Sản phẩm đã có giao dịch.\n Vui lòng kiểm tra lại thông tin."))
        self.bsd_bao_gia_id.write({
            'bsd_ngay_ky_bg': self.bsd_ngay_ky_bg,
            'state': 'da_ky'
        })
        self.bsd_bao_gia_id.bsd_unit_id.write({
            'state': 'dat_coc'
        })

