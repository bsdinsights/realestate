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


class BsdBaoGiaChonCK(models.TransientModel):
    _name = 'bsd.wizard.bao_gia.chon_ck'
    _description = 'Chọn chiết khấu áp dụng cho bảng tính giá'

    @api.model
    def default_get(self, fields_list):
        res = super(BsdBaoGiaChonCK, self).default_get(fields_list)
        bao_gia = self.env['bsd.bao_gia'].browse(self._context.get('active_ids', []))
        res.update({
            'bsd_bao_gia_id': bao_gia.id,
            'bsd_dot_mb_id': bao_gia.bsd_dot_mb_id.id,
            'bsd_cs_tt_id': bao_gia.bsd_cs_tt_id.id,
        })
        return res

    @api.onchange('bsd_bao_gia_id', 'bsd_dot_mb_id', 'bsd_cs_tt_id')
    def _onchange_ck(self):
        res = {}
        list_ck_chung = self.bsd_dot_mb_id.bsd_ck_ch_id.bsd_ct_ids.mapped('bsd_chiet_khau_id').ids or []
        list_ck_nb = self.bsd_dot_mb_id.bsd_ck_nb_id.bsd_ct_ids.mapped('bsd_chiet_khau_id').ids or []
        list_ck_pttt = self.bsd_dot_mb_id.bsd_ck_cstt_id.bsd_ct_ids.mapped('bsd_chiet_khau_id').ids or []
        res.update({
            'domain': {
                'bsd_ck_ch_ids': [('id', 'in', list_ck_chung)],
                'bsd_ck_nb_ids': [('id', 'in', list_ck_nb)],
                'bsd_ck_pttt_ids': [('id', 'in', list_ck_pttt)]
            }
        })
        return res

    bsd_bao_gia_id = fields.Many2one('bsd.bao_gia', string="Bảng tính giá")
    bsd_dot_mb_id = fields.Many2one('bsd.dot_mb', string="Đợt mở bán")
    bsd_cs_tt_id = fields.Many2one('bsd.cs_tt', string="Phương thức TT")
    bsd_ck_ch_ids = fields.Many2many('bsd.chiet_khau', relation="chung_rel", string="Chiết khấu chung")
    bsd_ck_nb_ids = fields.Many2many('bsd.chiet_khau', relation="noi_bo_rel", string="Chiết khấu nội bộ")
    bsd_ck_pttt_ids = fields.Many2many('bsd.chiet_khau', relation="pttt_rel", string="Chiết khấu theo PTTT")

    def action_xac_nhan(self):
        list_ps_ck = []
        for ck_ch in self.bsd_ck_ch_ids:
            list_ps_ck.append((0, 0, {'bsd_loai_ck': 'chung',
                                      'bsd_chiet_khau_id': ck_ch.id,
                                      'bsd_tien': ck_ch.bsd_tien_ck,
                                      'bsd_tl_ck': ck_ch.bsd_tl_ck,
                                      'bsd_ck_ch_id': self.bsd_dot_mb_id.bsd_ck_ch_id.id}))
        for ck_nb in self.bsd_ck_nb_ids:
            list_ps_ck.append((0, 0, {'bsd_loai_ck': 'noi_bo',
                                      'bsd_chiet_khau_id': ck_nb.id,
                                      'bsd_tien': ck_nb.bsd_tien_ck,
                                      'bsd_tl_ck': ck_nb.bsd_tl_ck,
                                      'bsd_ck_nb_id': self.bsd_dot_mb_id.bsd_ck_nb_id.id}))
        for ck_pttt in self.bsd_ck_pttt_ids:
            list_ps_ck.append((0, 0, {'bsd_loai_ck': 'ltt',
                                      'bsd_chiet_khau_id': ck_pttt.id,
                                      'bsd_tien': ck_pttt.bsd_tien_ck,
                                      'bsd_tl_ck': ck_pttt.bsd_tl_ck,
                                      'bsd_ck_cstt_id': self.bsd_dot_mb_id.bsd_ck_cstt_id.id,
                                      'bsd_cs_tt_id': self.bsd_cs_tt_id.id}))
        self.bsd_bao_gia_id.bsd_ps_ck_ids.unlink()
        self.bsd_bao_gia_id.write({
            'bsd_ps_ck_ids': list_ps_ck
        })


class BsdBaoGiaChonDKBG(models.TransientModel):
    _name = 'bsd.wizard.bao_gia.chon_dkbg'
    _description = 'Chọn điều kiện bàn giao áp dụng cho bảng tính giá'

    @api.model
    def default_get(self, fields_list):
        res = super(BsdBaoGiaChonDKBG, self).default_get(fields_list)
        bao_gia = self.env['bsd.bao_gia'].browse(self._context.get('active_ids', []))
        res.update({
            'bsd_bao_gia_id': bao_gia.id,
            'bsd_dot_mb_id': bao_gia.bsd_dot_mb_id.id,
            'bsd_unit_id': bao_gia.bsd_unit_id.id
        })
        return res

    @api.onchange('bsd_bao_gia_id', 'bsd_dot_mb_id', 'bsd_unit_id')
    def _onchange_ck(self):
        res = {}
        list_dk_bg_ids = self.bsd_dot_mb_id.bsd_dkbg_ids.filtered(
                lambda d: d.bsd_loai_sp_id == self.bsd_bao_gia_id.bsd_unit_id.bsd_loai_sp_id or not d.bsd_loai_sp_id)
        res.update({
            'domain': {
                'bsd_dk_bg_ids': [('id', 'in', list_dk_bg_ids.ids or [])],
            }
        })
        return res

    bsd_bao_gia_id = fields.Many2one('bsd.bao_gia', string="Bảng tính giá")
    bsd_dot_mb_id = fields.Many2one('bsd.dot_mb', string="Đợt mở bán")
    bsd_unit_id = fields.Many2one('product.product', string="Sản phẩm")
    bsd_dk_bg_ids = fields.Many2many('bsd.dk_bg', relation="dk_bg_rel", string="Điều kiện bàn giao")

    def action_xac_nhan(self):
        list_dk_bg = []
        for dk_bg in self.bsd_dk_bg_ids:
            list_dk_bg.append((0, 0, {
                                      'bsd_dk_bg_id': dk_bg.id,
                                      'bsd_dk_tt': dk_bg.bsd_dk_tt,
                                      'bsd_gia_m2': dk_bg.bsd_gia_m2,
                                      'bsd_tien': dk_bg.bsd_tien,
                                      'bsd_ty_le': dk_bg.bsd_ty_le}))
        self.bsd_bao_gia_id.bsd_bg_ids.unlink()
        self.bsd_bao_gia_id.write({
            'bsd_bg_ids': list_dk_bg
        })