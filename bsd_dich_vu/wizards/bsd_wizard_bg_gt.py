# -*- coding:utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError


class BsdKyBGGT(models.TransientModel):
    _name = 'bsd.wizard.ky_bg_gt'
    _description = 'Cập nhật ngày ký bàn giao giấy tờ'

    def _get_bao_giao(self):
        bg_gt = self.env['bsd.bg_gt'].browse(self._context.get('active_ids', []))
        return bg_gt

    bsd_bg_gt_id = fields.Many2one('bsd.bg_gt', string="Bàn giao giấy tờ", default=_get_bao_giao,
                                   readonly=True)
    bsd_ngay_bg_tt = fields.Datetime(string="Ngày bàn giao", required=True)
    bsd_nguoi_bg_tt_id = fields.Many2one('hr.employee', required=True, string="Người bàn giao")

    def action_xac_nhan(self):
        self.bsd_bg_gt_id.write({
            'bsd_ngay_bg_tt': self.bsd_ngay_bg_tt,
            'bsd_nguoi_bg_tt_id': self.bsd_nguoi_bg_tt_id.id,
            'state': 'ban_giao'
        })
        if self.bsd_bg_gt_id.bsd_hd_ban_id.state == 'ht_tt':
            self.bsd_bg_gt_id.bsd_hd_ban_id.write({
                'state': 'bt_gt',
            })
        self.bsd_bg_gt_id.bsd_unit_id.write({
            'bsd_ngay_hs': self.bsd_ngay_bg_tt,
            'bsd_bg_gt_id': self.bsd_bg_gt_id.id,
        })
