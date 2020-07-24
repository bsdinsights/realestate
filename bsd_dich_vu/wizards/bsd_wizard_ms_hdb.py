# -*- coding:utf-8 -*-

from odoo import models, fields, api, _

import logging
_logger = logging.getLogger(__name__)


class BsdMsHDB(models.TransientModel):
    _name = 'bsd.wizard.ms_hdb'
    _description = 'Chiết khấu mua sỉ cho hợp đồng'

    def _get_hdb(self):
        hdb = self.env['bsd.hd_ban'].browse(self._context.get('active_ids', []))
        return hdb

    bsd_hd_ban_id = fields.Many2one('bsd.hd_ban', string="Hợp đồng", default=_get_hdb, readonly=True)
    bsd_khach_hang_id = fields.Many2one(related='bsd_hd_ban_id.bsd_khach_hang_id')
    bsd_gia_truoc_thue = fields.Monetary(related='bsd_hd_ban_id.bsd_gia_truoc_thue')
    bsd_chiet_khau_id = fields.Many2one('bsd.chiet_khau', string="Chiết khấu mua sỉ")
    bsd_cach_tinh = fields.Selection(related="bsd_chiet_khau_id.bsd_cach_tinh", store=True)
    bsd_tien = fields.Monetary(string="Tiền chiết khấu")
    bsd_tl_ck = fields.Float(string="Tỷ lệ chiết khấu")
    bsd_tien_ck = fields.Monetary(string="Tiền chiết khấu", compute="_compute_tien_ck")
    bsd_hd_ban_ids = fields.Many2many('bsd.hd_ban', string="Hợp đồng")
    company_id = fields.Many2one('res.company', string='Công ty', default=lambda self: self.env.company)
    currency_id = fields.Many2one(related="company_id.currency_id", string="Tiền tệ", readonly=True)

    @api.depends('bsd_cach_tinh', 'bsd_tien', 'bsd_tl_ck', 'bsd_gia_truoc_thue')
    def _compute_tien_ck(self):
        for each in self:
            if each.bsd_cach_tinh == 'phan_tram':
                each.bsd_tien_ck = each.bsd_tl_ck * self.bsd_gia_truoc_thue / 100
            else:
                each.bsd_tien_ck = each.bsd_tien

    @api.onchange('bsd_hd_ban_id')
    def _onchange_hd_ban(self):
        list_ck_ms = self.bsd_hd_ban_id.bsd_dot_mb_id.bsd_ck_ms_id.bsd_ct_ids.mapped('bsd_chiet_khau_id').ids
        res = {}
        res.update({
            'domain': {
                'bsd_chiet_khau_id': [('id', 'in', list_ck_ms)]
            }
        })
        _logger.debug(res)
        return res

    @api.onchange('bsd_chiet_khau_id')
    def _onchange_ck(self):
        self.bsd_tien = self.bsd_chiet_khau_id.bsd_tien_ck
        self.bsd_tl_ck = self.bsd_chiet_khau_id.bsd_tl_ck

    def action_xac_nhan(self):
        self.bsd_hd_ban_id.tao_ck_ms(self.bsd_chiet_khau_id, tien=self.bsd_tien, tl_ck=self.bsd_tl_ck)
        # ghi nhận các hợp đồng đã tính mua sỉ
        self.bsd_hd_ban_id.write({
            'bsd_hd_ms_id': self.bsd_hd_ban_id.id,
        })
        self.bsd_hd_ban_ids.write({
            'bsd_hd_ms_id': self.bsd_hd_ban_id.id,
        })

