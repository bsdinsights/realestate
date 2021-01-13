# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.exceptions import UserError
import logging
_logger = logging.getLogger(__name__)


class BsdPsCk(models.Model):
    _name = 'bsd.ps_ck'
    _description = 'Thông tin phát sinh chiết khấu thương mại'
    _rec_name = 'bsd_chiet_khau_id'

    bsd_loai_ck = fields.Selection([('chung', 'Chung'),
                                    ('noi_bo', 'Nội bộ'),
                                    ('ltt', 'Phương thức TT')], string="Loại chiết khấu",
                                   default='chung', required=True, help="Loại chiết khấu")
    bsd_bao_gia_id = fields.Many2one('bsd.bao_gia', string="Báo giá", help="Tên báo giá")
    bsd_dat_coc_id = fields.Many2one('bsd.dat_coc', string="Đặt cọc", help="Tên Đặt cọc", readonly=True)
    bsd_ck_ch_id = fields.Many2one('bsd.ck_ch', string="Chiết khấu chung")
    bsd_ck_nb_id = fields.Many2one('bsd.ck_nb', string="Chiết khấu nội bộ")
    bsd_ck_cstt_id = fields.Many2one('bsd.ck_cstt', string="Chiết khấu CSTT")
    bsd_cs_tt_id = fields.Many2one('bsd.cs_tt', string="Chính sách thanh toán")
    bsd_chiet_khau_id = fields.Many2one('bsd.chiet_khau', string="Tên chiết khấu", help="Tên chiết khấu", required=True)
    bsd_ma_ck = fields.Char(related="bsd_chiet_khau_id.bsd_ma_ck", store=True)
    bsd_tu_ngay = fields.Date(string="Từ ngày", help="Ngày bắt đầu áp dụng chiết khấu",
                              related="bsd_chiet_khau_id.bsd_tu_ngay", store=True)
    bsd_den_ngay = fields.Date(string="Đến ngày", help="Ngày kết thúc áp dụng chiết khấu",
                               related="bsd_chiet_khau_id.bsd_den_ngay", store=True)
    bsd_cach_tinh = fields.Selection(related="bsd_chiet_khau_id.bsd_cach_tinh", store=True)
    bsd_tien = fields.Monetary(string="Tiền CK", help="Tiền chiết khấu được hưởng")
    bsd_tl_ck = fields.Float(string="Tỷ lệ CK", help="Tỷ lệ chiết khấu được hưởng")
    company_id = fields.Many2one('res.company', string='Công ty', default=lambda self: self.env.company)
    currency_id = fields.Many2one(related="company_id.currency_id", string="Tiền tệ", readonly=True)
    bsd_td_tt_id = fields.Many2one('bsd.dat_coc.td_tt', string="Thay đổi TT đặt cọc")

    @api.onchange('bsd_bao_gia_id')
    def _onchange_bao_gia(self):
        _logger.debug("onchange báo giá")
        self.bsd_ck_ch_id = self.bsd_bao_gia_id.bsd_dot_mb_id.bsd_ck_ch_id
        self.bsd_ck_cstt_id = self.bsd_bao_gia_id.bsd_dot_mb_id.bsd_ck_cstt_id
        self.bsd_ck_nb_id = self.bsd_bao_gia_id.bsd_dot_mb_id.bsd_ck_nb_id
        self.bsd_cs_tt_id = self.bsd_bao_gia_id.bsd_cs_tt_id

    @api.onchange('bsd_td_tt_id')
    def _onchange_td_tt(self):
        _logger.debug("onchange td_tt")
        self.bsd_ck_ch_id = self.bsd_td_tt_id.bsd_dot_mb_id.bsd_ck_ch_id
        self.bsd_ck_cstt_id = self.bsd_td_tt_id.bsd_dot_mb_id.bsd_ck_cstt_id
        self.bsd_ck_nb_id = self.bsd_td_tt_id.bsd_dot_mb_id.bsd_ck_nb_id

    @api.onchange('bsd_ck_ch_id', 'bsd_loai_ck', 'bsd_ck_cstt_id', 'bsd_ck_nb_id', 'bsd_cs_tt_id')
    def _onchange_ck(self):
        res = {}
        list_id = []
        _logger.debug("onchange phát sinh")
        _logger.debug(self.bsd_cs_tt_id)
        _logger.debug(self.bsd_ck_cstt_id)
        _logger.debug(self.bsd_loai_ck)
        if self.bsd_loai_ck == 'chung' and self.bsd_ck_ch_id:
            list_id = self.env['bsd.ck_ch_ct'].search([('bsd_ck_ch_id', '=', self.bsd_ck_ch_id.id)])\
                        .mapped('bsd_chiet_khau_id').ids
        if self.bsd_loai_ck == 'noi_bo' and self.bsd_ck_nb_id:
            list_id = self.env['bsd.ck_nb_ct'].search([('bsd_ck_nb_id', '=', self.bsd_ck_nb_id.id)])\
                        .mapped('bsd_chiet_khau_id').ids
        if self.bsd_loai_ck == 'ltt' and self.bsd_ck_cstt_id:
            list_id = self.env['bsd.ck_cstt_ct'].search([('bsd_ck_cstt_id', '=', self.bsd_ck_cstt_id.id)])\
                        .mapped('bsd_chiet_khau_id').filtered(lambda c: c.bsd_cs_tt_id == self.bsd_cs_tt_id).ids
        res.update({
            'domain': {
                'bsd_chiet_khau_id': [('id', 'in', list_id)]
            }
        })
        return res

    @api.onchange('bsd_chiet_khau_id')
    def _onchange_chiet_khau(self):
        self.bsd_tien = self.bsd_chiet_khau_id.bsd_tien_ck
        self.bsd_tl_ck = self.bsd_chiet_khau_id.bsd_tl_ck

    # R.31
    @api.depends('bsd_cach_tinh', 'bsd_tien', 'bsd_tl_ck', 'bsd_bao_gia_id.bsd_gia_ban', 'bsd_bao_gia_id.bsd_tien_bg')
    def _compute_tien_ck(self):
        for each in self:
            if each.bsd_cach_tinh == 'phan_tram':
                each.bsd_tien_ck = each.bsd_tl_ck * \
                                   (each.bsd_bao_gia_id.bsd_gia_ban + each.bsd_bao_gia_id.bsd_tien_bg) / 100
            else:
                each.bsd_tien_ck = each.bsd_tien
