# -*- coding:utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError


class BsdKyBGGT(models.TransientModel):
    _name = 'bsd.wizard.ky_tl_kt_hd'
    _description = 'Thanh lý kết thúc hợp đồng'

    def _get_tl(self):
        tl_kt_hd = self.env['bsd.tl_kt_hd'].browse(self._context.get('active_ids', []))
        return tl_kt_hd

    bsd_tl_kt_hd_id = fields.Many2one('bsd.tl_kt_hd', string="Thanh lý kết thúc hợp đồng", default=_get_tl,
                                      readonly=True)
    bsd_ngay_xn = fields.Date(string="Ngày ký", required=True)

    def action_xac_nhan(self):
        self.bsd_tl_kt_hd_id.write({
            'bsd_ngay_xn': self.bsd_ngay_xn,
            'bsd_nguoi_xn_id': self.env.uid,
            'state': 'da_tl'
        })
        if self.bsd_tl_kt_hd_id.bsd_hd_ban_id.state == '10_bg_gt':
            self.bsd_tl_kt_hd_id.bsd_hd_ban_id.write({
                'state': '11_da_ht',
            })
        # if self.bsd_tl_kt_hd_id.bsd_unit_id.state == 'ht_tt':
        #     self.bsd_tl_kt_hd_id.bsd_unit_id.write({
        #         'state': 'da_ht',
        #     })
