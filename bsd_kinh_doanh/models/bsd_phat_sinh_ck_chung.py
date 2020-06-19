# -*- coding: utf-8 -*-

from odoo import models, fields, api


class BsdPsCkChung(models.Model):
    _name = 'bsd.ps_ck_ch'
    _description = 'Thông tin tiền chiết khấu'

    bsd_bao_gia_id = fields.Many2one('bsd.bao_gia', string="Báo giá", help="Tên báo giá")
    bsd_ck_ch_id = fields.Many2one('bsd.ck_ch', string="Chiết khấu chung", required=True)
    bsd_chiet_khau_id = fields.Many2one('bsd.chiet_khau', string="Mã chiết khấu", help="Mã chiết khấu", required=True)
    bsd_ten_ck = fields.Char(related="bsd_chiet_khau_id.bsd_ten_ck", store=True)
    bsd_tu_ngay = fields.Date(string="Từ ngày", help="Ngày bắt đầu áp dụng chiết khấu",
                              related="bsd_chiet_khau_id.bsd_tu_ngay", store=True)
    bsd_den_ngay = fields.Date(string="Đến ngày", help="Ngày kết thúc áp dụng chiết khấu",
                               related="bsd_chiet_khau_id.bsd_den_ngay", store=True)
    bsd_cach_tinh = fields.Selection(related="bsd_chiet_khau_id.bsd_cach_tinh", store=True)
    bsd_tl_ck = fields.Float(related="bsd_chiet_khau_id.bsd_tl_ck", store=True)
    bsd_tien = fields.Monetary(related="bsd_chiet_khau_id.bsd_tien_ck", string="Tiền", store=True)
    bsd_tien_ck = fields.Monetary(string="Tiền chiết khấu",
                                  compute="_compute_tien_ck", store=True,
                                  help="Tiền bàn giao theo chiết khấu")
    bsd_loai_ck = fields.Selection(related="bsd_chiet_khau_id.bsd_loai_ck", store=True)
    company_id = fields.Many2one('res.company', string='Công ty', default=lambda self: self.env.company)
    currency_id = fields.Many2one(related="company_id.currency_id", string="Tiền tệ", readonly=True)

    @api.onchange('bsd_bao_gia_id')
    def _onchange_bao_gia(self):
        self.bsd_ck_ch_id = self.bsd_bao_gia_id.bsd_dot_mb_id.bsd_ck_ch_id

    @api.onchange('bsd_ck_ch_id')
    def _onchange_ck(self):
        res = {}
        list_id = []
        if self.bsd_ck_ch_id:
            list_id = self.env['bsd.ck_ch_ct'].search([('bsd_ck_ch_id', '=', self.bsd_ck_ch_id.id)])\
                        .mapped('bsd_chiet_khau_id').ids
        res.update({
            'domain': {
                'bsd_chiet_khau_id': [('id', 'in', list_id)]
            }
        })
        return res

    @api.depends('bsd_cach_tinh', 'bsd_tien', 'bsd_tl_ck', 'bsd_bao_gia_id.bsd_gia_ban')
    def _compute_tien_ck(self):
        for each in self:
            if each.bsd_cach_tinh == 'phan_tram':
                each.bsd_tien_ck = each.bsd_tl_ck * each.bsd_bao_gia_id.bsd_gia_ban / 100
            else:
                each.bsd_tien_ck = each.bsd_tien
