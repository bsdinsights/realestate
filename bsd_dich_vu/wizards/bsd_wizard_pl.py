# -*- coding:utf-8 -*-

from odoo import models, fields, api, _
from odoo.tools.float_utils import float_round
import logging
_logger = logging.getLogger(__name__)


class BsdKyPL(models.TransientModel):
    _name = 'bsd.wizard.ky_pl'
    _description = 'Xác nhận ngày ký phụ lục'

    @api.model
    def default_get(self, fields_list):
        res = super(BsdKyPL, self).default_get(fields_list)
        _logger.debug(self._context)
        if self._context.get('active_model', []) == 'bsd.pl_cktm':
            pl_cktm = self.env['bsd.pl_cktm'].browse(self._context.get('active_ids', []))
            res.update({
                'bsd_loai_pl': 'cktm',
                'bsd_pl_cktm_id': pl_cktm.id
            })
        elif self._context.get('active_model', []) == 'bsd.pl_pttt':
            pl_pttt = self.env['bsd.pl_pttt'].browse(self._context.get('active_ids', []))
            res.update({
                'bsd_loai_pl': 'pttt',
                'bsd_pl_pttt_id': pl_pttt.id
            })
        elif self._context.get('active_model', []) == 'bsd.pl_dkbg':
            pl_dkbg = self.env['bsd.pl_dkbg'].browse(self._context.get('active_ids', []))
            res.update({
                'bsd_loai_pl': 'dkbg',
                'bsd_pl_dkbg_id': pl_dkbg.id
            })
        elif self._context.get('active_model', []) == 'bsd.pl_qsdd':
            pl_qsdd = self.env['bsd.pl_qsdd'].browse(self._context.get('active_ids', []))
            res.update({
                'bsd_loai_pl': 'qsdd',
                'bsd_pl_qsdd_id': pl_qsdd.id
            })
        elif self._context.get('active_model', []) == 'bsd.pl_tti':
            pl_tti = self.env['bsd.pl_tti'].browse(self._context.get('active_ids', []))
            res.update({
                'bsd_loai_pl': 'tti',
                'bsd_pl_tti_id': pl_tti.id
            })
        elif self._context.get('active_model', []) == 'bsd.pl_cldt':
            pl_cldt = self.env['bsd.pl_cldt'].browse(self._context.get('active_ids', []))
            res.update({
                'bsd_loai_pl': 'cldt',
                'bsd_pl_cldt_id': pl_cldt.id
            })
        return res

    bsd_pl_pttt_id = fields.Many2one('bsd.pl_pttt', string="Phụ lục", readonly=True)
    bsd_pl_cktm_id = fields.Many2one('bsd.pl_cktm', string="Phụ lục", readonly=True)
    bsd_pl_dkbg_id = fields.Many2one('bsd.pl_dkbg', string="Phụ lục", readonly=True)
    bsd_pl_qsdd_id = fields.Many2one('bsd.pl_qsdd', string="Phụ lục", readonly=True)
    bsd_ngay_ky_pl = fields.Date(string="Ngày ký phụ lục", required=True)
    bsd_pl_tti_id = fields.Many2one('bsd.pl_tti', string="Phụ lục", readonly=True)
    bsd_pl_cldt_id = fields.Many2one('bsd.pl_cldt', string="Phụ lục", readonly=True)
    bsd_loai_pl = fields.Selection([('pttt', 'PTTT'), ('cktm', 'CKTM'),
                                    ('dkbg', 'ĐKBG'), ('qsdd', 'QSDĐ'),
                                    ('tti', 'Thay đổi thông tin'),
                                    ('cldt', 'Chênh lệch diện tích')])

    def action_xac_nhan(self):
        if self.bsd_pl_pttt_id:
            self.bsd_pl_pttt_id.write({
                'bsd_ngay_ky_pl': self.bsd_ngay_ky_pl,
                'bsd_nguoi_xn_ky_id': self.env.uid,
                'state': 'dk_pl',
            })
            self.bsd_pl_pttt_id.thay_doi_pttt()
        if self.bsd_pl_cktm_id:
            self.bsd_pl_cktm_id.write({
                'bsd_ngay_ky_pl': self.bsd_ngay_ky_pl,
                'bsd_nguoi_xn_ky_id': self.env.uid,
                'state': 'dk_pl',
            })
            self.bsd_pl_cktm_id.thay_doi_cktm()
        if self.bsd_pl_dkbg_id:
            self.bsd_pl_dkbg_id.write({
                'bsd_ngay_ky_pl': self.bsd_ngay_ky_pl,
                'bsd_nguoi_xn_ky_id': self.env.uid,
                'state': 'dk_pl',
            })
            self.bsd_pl_dkbg_id.thay_doi_dkbg()
        if self.bsd_pl_qsdd_id:
            self.bsd_pl_qsdd_id.write({
                'bsd_ngay_ky_pl': self.bsd_ngay_ky_pl,
                'bsd_nguoi_xn_ky_id': self.env.uid,
                'state': 'dk_pl',
            })
            self.bsd_pl_qsdd_id.thay_doi_qsdd()
        if self.bsd_pl_tti_id:
            self.bsd_pl_tti_id.write({
                'bsd_ngay_ky_pl': self.bsd_ngay_ky_pl,
                'bsd_nguoi_xn_ky_id': self.env.uid,
                'state': 'dk_pl',
            })
        if self.bsd_pl_cldt_id:
            self.bsd_pl_cldt_id.write({
                'bsd_ngay_ky_pl': self.bsd_ngay_ky_pl,
                'bsd_nguoi_xn_ky_id': self.env.uid,
                'state': 'dk_pl',
            })
            self.bsd_pl_cldt_id.thay_doi_cldt()


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
        elif self._context.get('active_model', []) == 'bsd.pl_pttt':
            pl_pttt = self.env['bsd.pl_pttt'].browse(self._context.get('active_ids', []))
            res.update({
                'bsd_loai_pl': 'pttt',
                'bsd_pl_pttt_id': pl_pttt.id
            })
        elif self._context.get('active_model', []) == 'bsd.pl_dkbg':
            pl_dkbg = self.env['bsd.pl_dkbg'].browse(self._context.get('active_ids', []))
            res.update({
                'bsd_loai_pl': 'dkbg',
                'bsd_pl_dkbg_id': pl_dkbg.id
            })
        elif self._context.get('active_model', []) == 'bsd.pl_qsdd':
            pl_qsdd = self.env['bsd.pl_qsdd'].browse(self._context.get('active_ids', []))
            res.update({
                'bsd_loai_pl': 'qsdd',
                'bsd_pl_qsdd_id': pl_qsdd.id
            })
        elif self._context.get('active_model', []) == 'bsd.pl_tti':
            pl_tti = self.env['bsd.pl_tti'].browse(self._context.get('active_ids', []))
            res.update({
                'bsd_loai_pl': 'tti',
                'bsd_pl_tti_id': pl_tti.id
            })
        elif self._context.get('active_model', []) == 'bsd.pl_cldt':
            pl_cldt = self.env['bsd.pl_cldt'].browse(self._context.get('active_ids', []))
            res.update({
                'bsd_loai_pl': 'cldt',
                'bsd_pl_cldt_id': pl_cldt.id
            })
        return res

    bsd_pl_pttt_id = fields.Many2one('bsd.pl_pttt', string="Phụ lục", readonly=True)
    bsd_pl_cktm_id = fields.Many2one('bsd.pl_cktm', string="Phụ lục", readonly=True)
    bsd_pl_dkbg_id = fields.Many2one('bsd.pl_dkbg', string="Phụ lục", readonly=True)
    bsd_pl_qsdd_id = fields.Many2one('bsd.pl_qsdd', string="Phụ lục", readonly=True)
    bsd_pl_tti_id = fields.Many2one('bsd.pl_tti', string="Phụ lục", readonly=True)
    bsd_pl_cldt_id = fields.Many2one('bsd.pl_cldt', string="Phụ lục", readonly=True)
    bsd_loai_pl = fields.Selection([('pttt', 'PTTT'), ('cktm', 'CKTM'),
                                    ('dkbg', 'ĐKBG'), ('qsdd', 'QSDĐ'),
                                    ('tti', 'Thay đổi thông tin'),
                                    ('cldt', 'Chênh lệch diện tích')])
    bsd_ly_do = fields.Char(string="Lý do", required=True)

    def action_xac_nhan(self):
        if self.bsd_pl_pttt_id:
            self.bsd_pl_pttt_id.write({
                'bsd_ly_do': self.bsd_ly_do,
                'state': 'nhap',
            })
        elif self.bsd_pl_cktm_id:
            self.bsd_pl_cktm_id.write({
                'bsd_ly_do': self.bsd_ly_do,
                'state': 'nhap',
            })
        elif self.bsd_pl_dkbg_id:
            self.bsd_pl_dkbg_id.write({
                'bsd_ly_do': self.bsd_ly_do,
                'state': 'nhap',
            })
        elif self.bsd_pl_qsdd_id:
            self.bsd_pl_qsdd_id.write({
                'bsd_ly_do': self.bsd_ly_do,
                'state': 'nhap',
            })
        elif self.bsd_pl_tti_id:
            self.bsd_pl_tti_id.write({
                'bsd_ly_do': self.bsd_ly_do,
                'state': 'nhap',
            })
        elif self.bsd_pl_cldt_id:
            self.bsd_pl_cldt_id.write({
                'bsd_ly_do': self.bsd_ly_do,
                'state': 'nhap',
            })


class BsdHuytPL(models.TransientModel):
    _name = 'bsd.wizard.huy_pl'
    _description = 'Ghi nhận lý do hủy phụ lục'

    @api.model
    def default_get(self, fields_list):
        _logger.debug(self._context)
        res = super(BsdHuytPL, self).default_get(fields_list)
        _logger.debug(self._context)
        if self._context.get('active_model', []) == 'bsd.pl_cktm':
            pl_cktm = self.env['bsd.pl_cktm'].browse(self._context.get('active_ids', []))
            res.update({
                'bsd_loai_pl': 'cktm',
                'bsd_pl_cktm_id': pl_cktm.id
            })
        elif self._context.get('active_model', []) == 'bsd.pl_pttt':
            pl_pttt = self.env['bsd.pl_pttt'].browse(self._context.get('active_ids', []))
            res.update({
                'bsd_loai_pl': 'pttt',
                'bsd_pl_pttt_id': pl_pttt.id
            })
        elif self._context.get('active_model', []) == 'bsd.pl_dkbg':
            pl_dkbg = self.env['bsd.pl_dkbg'].browse(self._context.get('active_ids', []))
            res.update({
                'bsd_loai_pl': 'dkbg',
                'bsd_pl_dkbg_id': pl_dkbg.id
            })
        elif self._context.get('active_model', []) == 'bsd.pl_qsdd':
            pl_qsdd = self.env['bsd.pl_qsdd'].browse(self._context.get('active_ids', []))
            res.update({
                'bsd_loai_pl': 'qsdd',
                'bsd_pl_qsdd_id': pl_qsdd.id
            })
        elif self._context.get('active_model', []) == 'bsd.pl_tti':
            pl_tti = self.env['bsd.pl_tti'].browse(self._context.get('active_ids', []))
            res.update({
                'bsd_loai_pl': 'tti',
                'bsd_pl_tti_id': pl_tti.id
            })
        elif self._context.get('active_model', []) == 'bsd.pl_cldt':
            pl_cldt = self.env['bsd.pl_cldt'].browse(self._context.get('active_ids', []))
            res.update({
                'bsd_loai_pl': 'cldt',
                'bsd_pl_cldt_id': pl_cldt.id
            })
        return res

    bsd_pl_pttt_id = fields.Many2one('bsd.pl_pttt', string="Phụ lục", readonly=True)
    bsd_pl_cktm_id = fields.Many2one('bsd.pl_cktm', string="Phụ lục", readonly=True)
    bsd_pl_dkbg_id = fields.Many2one('bsd.pl_dkbg', string="Phụ lục", readonly=True)
    bsd_pl_qsdd_id = fields.Many2one('bsd.pl_qsdd', string="Phụ lục", readonly=True)
    bsd_pl_tti_id = fields.Many2one('bsd.pl_tti', string="Phụ lục", readonly=True)
    bsd_pl_cldt_id = fields.Many2one('bsd.pl_cldt', string="Phụ lục", readonly=True)
    bsd_loai_pl = fields.Selection([('pttt', 'PTTT'), ('cktm', 'CKTM'),
                                    ('dkbg', 'ĐKBG'), ('qsdd', 'QSDĐ'),
                                    ('tti', 'Thay đổi thông tin'),
                                    ('cldt', 'Chênh lệch diện tích')])
    bsd_ly_do = fields.Char(string="Lý do", required=True)

    def action_xac_nhan(self):
        if self.bsd_pl_pttt_id:
            self.bsd_pl_pttt_id.write({
                'bsd_ly_do_huy': self.bsd_ly_do,
                'state': 'huy',
                'bsd_ngay_huy': fields.Date.today(),
                'bsd_nguoi_huy_id': self.env.uid
            })
        elif self.bsd_pl_cktm_id:
            self.bsd_pl_cktm_id.write({
                'bsd_ly_do_huy': self.bsd_ly_do,
                'state': 'huy',
                'bsd_ngay_huy': fields.Date.today(),
                'bsd_nguoi_huy_id': self.env.uid
            })
        elif self.bsd_pl_dkbg_id:
            self.bsd_pl_dkbg_id.write({
                'bsd_ly_do_huy': self.bsd_ly_do,
                'state': 'huy',
                'bsd_ngay_huy': fields.Date.today(),
                'bsd_nguoi_huy_id': self.env.uid
            })
        elif self.bsd_pl_qsdd_id:
            self.bsd_pl_qsdd_id.write({
                'bsd_ly_do_huy': self.bsd_ly_do,
                'state': 'huy',
                'bsd_ngay_huy': fields.Date.today(),
                'bsd_nguoi_huy_id': self.env.uid
            })
        elif self.bsd_pl_tti_id:
            self.bsd_pl_tti_id.write({
                'bsd_ly_do_huy': self.bsd_ly_do,
                'state': 'huy',
                'bsd_ngay_huy': fields.Date.today(),
                'bsd_nguoi_huy_id': self.env.uid
            })
        elif self.bsd_pl_cldt_id:
            self.bsd_pl_cldt_id.write({
                'bsd_ly_do_huy': self.bsd_ly_do,
                'state': 'huy',
                'bsd_ngay_huy': fields.Date.today(),
                'bsd_nguoi_huy_id': self.env.uid
            })


class BsdPLChonDKBG(models.TransientModel):
    _name = 'bsd.wizard.phu_luc.chon_dkbg'
    _description = 'Chọn điều kiện bàn giao mới cho hợp đồng'

    @api.model
    def default_get(self, fields_list):
        res = super(BsdPLChonDKBG, self).default_get(fields_list)
        pl = self.env['bsd.pl_dkbg'].browse(self._context.get('active_ids', []))
        res.update({
            'bsd_pl_dkbg_id': pl.id,
            'bsd_dk_bg_ids': [(6, 0, pl.bsd_dkbg_moi_ids.ids)]
        })
        return res

    @api.onchange('bsd_pl_dkbg_id')
    def _onchange_ck(self):
        dot_mb = self.bsd_pl_dkbg_id.bsd_hd_ban_id.bsd_dot_mb_id
        unit = self.bsd_pl_dkbg_id.bsd_unit_id
        res = {}
        list_dk_bg_ids = dot_mb.bsd_dkbg_ids.filtered(
                lambda d: d.bsd_loai_sp_id == unit.bsd_loai_sp_id or not d.bsd_loai_sp_id)
        res.update({
            'domain': {
                'bsd_dk_bg_ids': [('id', 'in', list_dk_bg_ids.ids or [])],
            }
        })
        return res

    bsd_pl_dkbg_id = fields.Many2one('bsd.pl_dkbg', string="Phụ lục")
    bsd_dk_bg_ids = fields.Many2many('bsd.dk_bg', relation="bsd_wizard_dk_bg_rel", string="Điều kiện bàn giao")

    def action_xac_nhan(self):
        tien_bg = 0
        tien_ck = 0
        dt_sd = self.bsd_pl_dkbg_id.bsd_unit_id.bsd_dt_sd
        # Cập nhật giá trị tiền bàn giao mới
        for dk_bg in self.bsd_dk_bg_ids:
            if dk_bg.bsd_dk_tt == 'm2':
                tien_bg += dk_bg.bsd_gia_m2 * dt_sd
            elif dk_bg.bsd_dk_tt == 'tien':
                tien_bg += dk_bg.bsd_tien
            else:
                tien_bg += float_round(dk_bg.bsd_ty_le * self.bsd_pl_dkbg_id.bsd_gia_ban_moi / 100, 0)
        # Cập nhật giá trị chiết khấu giao dịch mới
        ck_gd_ids = self.bsd_pl_dkbg_id.bsd_hd_ban_id.bsd_ps_gd_ck_ids
        for ck_gd in ck_gd_ids:
            tien_ck += float_round(ck_gd.bsd_tl_ck * (self.bsd_pl_dkbg_id.bsd_gia_ban_moi + tien_bg) / 100, 0) \
                       + ck_gd.bsd_tien
        self.bsd_pl_dkbg_id.write({
            'bsd_dkbg_moi_ids': [(6, 0, self.bsd_dk_bg_ids.ids)],
            'bsd_tien_bg_moi': tien_bg,
            'bsd_tien_ck_moi': tien_ck
        })
