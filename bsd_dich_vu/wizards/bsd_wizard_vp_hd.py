# -*- coding:utf-8 -*-

from odoo import models, fields, api, _

import logging
_logger = logging.getLogger(__name__)


class BsdWizardKhongDuyetVPHD(models.TransientModel):
    _name = 'bsd.wizard.khong_duyet.vp_hd'
    _description = 'Ghi nhận lý do từ chối'

    def _get_vp_hd(self):
        vp_hd = self.env['bsd.vp_hd'].browse(self._context.get('active_ids', []))
        return vp_hd

    bsd_vp_hd_id = fields.Many2one('bsd.vp_hd', string="Vi phạm HĐ", default=_get_vp_hd, readonly=True)
    bsd_ly_do = fields.Char(string="Lý do", required=True)

    def action_xac_nhan(self):
        self.bsd_vp_hd_id.write({
            'bsd_ly_do': self.bsd_ly_do,
            'state': 'nhap',
        })
        self.bsd_vp_hd_id.message_post(body='Lý do không duyệt: ' + self.bsd_ly_do)


class BsdWizardKyVPHD(models.TransientModel):
    _name = 'bsd.wizard.ky.vp_hd'
    _description = 'Ghi nhận ngày ký thực sự của khách hàng'

    def _get_vp_hd(self):
        vp_hd = self.env['bsd.vp_hd'].browse(self._context.get('active_ids', []))
        return vp_hd

    bsd_vp_hd_id = fields.Many2one('bsd.vp_hd', string="Vi phạm HĐ", default=_get_vp_hd, readonly=True)
    bsd_ngay_ky = fields.Date(string="Ngày ký", required=True)

    def action_xac_nhan(self):
        self.bsd_vp_hd_id.write({
            'bsd_ngay_ky': self.bsd_ngay_ky,
            'bsd_nguoi_xn_ky_id': self.env.uid,
            'state': 'da_ky',
        })
        self.bsd_vp_hd_id.action_xu_ly()