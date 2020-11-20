# -*- coding:utf-8 -*-

from odoo import models, fields, api, _

import logging
_logger = logging.getLogger(__name__)


class BsdKyPL(models.TransientModel):
    _name = 'bsd.wizard.ky_pl'
    _description = 'Xác nhận ngày ký phụ lục thay đổi phương thức thanh toán'

    @api.model
    def default_get(self, fields_list):
        _logger.debug(self._context)
        res = super(BsdKyPL, self).default_get(fields_list)
        _logger.debug(self._context)
        if self._context.get('active_model', []) == 'bsd.pl_cktm':
            pl_cktm = self.env['bsd.pl_cktm'].browse(self._context.get('active_ids', []))
            res.update({
                'bsd_loai_pl': 'cktm',
                'bsd_pl_cktm_id': pl_cktm.id
            })
        if self._context.get('active_model', []) == 'bsd.pl_pttt':
            pl_pttt = self.env['bsd.pl_pttt'].browse(self._context.get('active_ids', []))
            res.update({
                'bsd_loai_pl': 'pttt',
                'bsd_pl_pttt_id': pl_pttt.id
            })
        return res

    bsd_pl_pttt_id = fields.Many2one('bsd.pl_pttt', string="Phụ lục", readonly=True)
    bsd_pl_cktm_id = fields.Many2one('bsd.pl_cktm', string="Phụ lục", readonly=True)
    bsd_ngay_ky_pl = fields.Date(string="Ngày ký phụ lục", required=True)
    bsd_loai_pl = fields.Selection([('pttt', 'PTTT'), ('cktm', 'CKTM')])

    def action_xac_nhan(self):
        self.bsd_pl_pttt_id.write({
            'bsd_ngay_ky_pl': self.bsd_ngay_ky_pl,
            'bsd_nguoi_xn_ky_id': self.env.uid,
            'state': 'dk_pl',
        })
        self.bsd_pl_pttt_id.thay_doi_pttt()


class BsdKhongDuyetPL(models.TransientModel):
    _name = 'bsd.wizard.khong_duyet_pl'
    _description = 'Ghi nhận lý do từ chối'

    @api.model
    def default_get(self, fields_list):
        _logger.debug(self._context)
        res = super(BsdKhongDuyetPL, self).default_get(fields_list)
        _logger.debug(self._context)
        if self._context.get('active_model', []) == 'bsd.pl_cktm':
            pl_cktm = self.env['bsd.pl_cktm'].browse(self._context.get('active_ids', []))
            res.update({
                'bsd_loai_pl': 'cktm',
                'bsd_pl_cktm_id': pl_cktm.id
            })
        if self._context.get('active_model', []) == 'bsd.pl_pttt':
            pl_pttt = self.env['bsd.pl_pttt'].browse(self._context.get('active_ids', []))
            res.update({
                'bsd_loai_pl': 'pttt',
                'bsd_pl_pttt_id': pl_pttt.id
            })
        return res

    bsd_pl_pttt_id = fields.Many2one('bsd.pl_pttt', string="Phụ lục", readonly=True)
    bsd_pl_cktm_id = fields.Many2one('bsd.pl_cktm', string="Phụ lục", readonly=True)
    bsd_loai_pl = fields.Selection([('pttt', 'PTTT'), ('cktm', 'CKTM')])
    bsd_ly_do = fields.Char(string="Lý do", required=True)

    def action_xac_nhan(self):
        if self.bsd_pl_pttt_id:
            self.bsd_pl_pttt_id.write({
                'bsd_ly_do': self.bsd_ly_do,
                'state': 'nhap',
            })
        if self.bsd_pl_cktm_id:
            self.bsd_pl_cktm_id.write({
                'bsd_ly_do': self.bsd_ly_do,
                'state': 'nhap',
            })


class BsdHuytPLPTTT(models.TransientModel):
    _name = 'bsd.wizard.huy_pl'
    _description = 'Ghi nhận lý do hủy phụ lục thay đổi phương thức thanh toán'

    @api.model
    def default_get(self, fields_list):
        _logger.debug(self._context)
        res = super(BsdHuytPLPTTT, self).default_get(fields_list)
        _logger.debug(self._context)
        if self._context.get('active_model', []) == 'bsd.pl_cktm':
            pl_cktm = self.env['bsd.pl_cktm'].browse(self._context.get('active_ids', []))
            res.update({
                'bsd_loai_pl': 'cktm',
                'bsd_pl_cktm_id': pl_cktm.id
            })
        if self._context.get('active_model', []) == 'bsd.pl_pttt':
            pl_pttt = self.env['bsd.pl_pttt'].browse(self._context.get('active_ids', []))
            res.update({
                'bsd_loai_pl': 'pttt',
                'bsd_pl_pttt_id': pl_pttt.id
            })
        return res

    bsd_pl_pttt_id = fields.Many2one('bsd.pl_pttt', string="Phụ lục", readonly=True)
    bsd_pl_cktm_id = fields.Many2one('bsd.pl_cktm', string="Phụ lục", readonly=True)
    bsd_ly_do = fields.Char(string="Lý do", required=True)
    bsd_loai_pl = fields.Selection([('pttt', 'PTTT'), ('cktm', 'CKTM')])

    def action_xac_nhan(self):
        if self.bsd_pl_pttt_id:
            self.bsd_pl_pttt_id.write({
                'bsd_ly_do_huy': self.bsd_ly_do,
                'state': 'huy',
                'bsd_ngay_huy': fields.Date.today(),
                'bsd_nguoi_huy_id': self.env.uid
            })
        if self.bsd_pl_cktm_id:
            self.bsd_pl_cktm_id.write({
                'bsd_ly_do_huy': self.bsd_ly_do,
                'state': 'huy',
                'bsd_ngay_huy': fields.Date.today(),
                'bsd_nguoi_huy_id': self.env.uid
            })
