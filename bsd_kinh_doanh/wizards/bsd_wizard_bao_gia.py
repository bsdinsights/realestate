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

    bsd_bao_gia_id = fields.Many2one('bsd.bao_gia', string="Bảng tính giá", default=_get_bg, readonly=True)
    bsd_ngay_ky_bg = fields.Date(string="Ngày ký BTG", required=True)

    def action_xac_nhan(self):
        # Kiểm tra trạng thái unit trước khi ký bảng tính giá
        if self.bsd_bao_gia_id.bsd_unit_id.state not in ['giu_cho', 'san_sang']:
            raise UserError(_("Sản phẩm đã có giao dịch.\n Vui lòng kiểm tra lại thông tin."))
        self.bsd_bao_gia_id.write({
            'bsd_ngay_ky_bg': self.bsd_ngay_ky_bg,
            'state': 'da_ky'
        })
        self.bsd_bao_gia_id.bsd_unit_id.sudo().write({
            'state': 'dat_coc'
        })


class BsdBaoGiaChonCK(models.TransientModel):
    _name = 'bsd.wizard.bao_gia.chon_ck'
    _description = 'Chọn chiết khấu áp dụng cho bảng tính giá'

    @api.model
    def default_get(self, fields_list):
        res = super(BsdBaoGiaChonCK, self).default_get(fields_list)
        _logger.debug(self._context)
        if self._context.get('active_model') == 'bsd.bao_gia':
            bao_gia = self.env['bsd.bao_gia'].browse(self._context.get('active_ids', []))
            res.update({
                'bsd_bao_gia_id': bao_gia.id,
                'bsd_loai': 'bao_gia',
                'bsd_dot_mb_id': bao_gia.bsd_dot_mb_id.id,
                'bsd_cs_tt_id': bao_gia.bsd_cs_tt_id.id,
                'bsd_ck_ch_ids': [(6, 0, bao_gia.bsd_ps_ck_ids
                                   .filtered(lambda x: x.bsd_loai_ck == 'chung')
                                   .mapped('bsd_chiet_khau_id').ids)],
                'bsd_ck_nb_ids': [(6, 0, bao_gia.bsd_ps_ck_ids
                                   .filtered(lambda x: x.bsd_loai_ck == 'noi_bo')
                                   .mapped('bsd_chiet_khau_id').ids)],
                'bsd_ck_pttt_ids': [(6, 0, bao_gia.bsd_ps_ck_ids
                                     .filtered(lambda x: x.bsd_loai_ck == 'ltt')
                                     .mapped('bsd_chiet_khau_id').ids)]
            })
        # Gọi từ thay đổi thông tin thay đổi chiết khấu thương mại
        elif self._context.get('active_model') == 'bsd.dat_coc.td_tt' and self._context.get('loai') != 'ltt':
            td_tt = self.env['bsd.dat_coc.td_tt'].browse(self._context.get('active_ids', []))
            res.update({
                'bsd_td_tt_id': td_tt.id,
                'bsd_loai': 'td_tt',
                'bsd_dot_mb_id': td_tt.bsd_dot_mb_id.id,
                'bsd_cs_tt_id': td_tt.bsd_dat_coc_id.bsd_cs_tt_id.id,
                'bsd_ck_ch_ids': [(6, 0, td_tt.bsd_ps_ck_ht_ids
                                   .filtered(lambda x: x.bsd_loai_ck == 'chung')
                                   .mapped('bsd_chiet_khau_id').ids)],
                'bsd_ck_nb_ids': [(6, 0, td_tt.bsd_ps_ck_ht_ids
                                   .filtered(lambda x: x.bsd_loai_ck == 'noi_bo')
                                   .mapped('bsd_chiet_khau_id').ids)],
                'bsd_ck_pttt_ids': [(6, 0, td_tt.bsd_ps_ck_ht_ids
                                     .filtered(lambda x: x.bsd_loai_ck == 'ltt')
                                     .mapped('bsd_chiet_khau_id').ids)]
            })
        # Gọi từ thay đổi thông tin thay đổi phương thức thanh toán
        elif self._context.get('active_model') == 'bsd.dat_coc.td_tt' and self._context.get('loai') == 'ltt':
            td_tt = self.env['bsd.dat_coc.td_tt'].browse(self._context.get('active_ids', []))
            res.update({
                'bsd_td_tt_id': td_tt.id,
                'bsd_dot_mb_id': td_tt.bsd_dot_mb_id.id,
                'bsd_cs_tt_id': td_tt.bsd_dat_coc_id.bsd_cs_tt_id.id,
                'bsd_loai': 'td_tt_pttt',
            })
        return res

    @api.onchange('bsd_dot_mb_id', 'bsd_cs_tt_id')
    def _onchange_ck(self):
        res = {}
        list_ck_chung = self.bsd_dot_mb_id.bsd_ck_ch_id.bsd_ct_ids.mapped('bsd_chiet_khau_id').ids or []
        list_ck_nb = self.bsd_dot_mb_id.bsd_ck_nb_id.bsd_ct_ids.mapped('bsd_chiet_khau_id').ids or []
        list_ck_pttt = self.bsd_dot_mb_id.bsd_ck_cstt_id.bsd_ct_ids.mapped('bsd_chiet_khau_id')\
                           .filtered(lambda x: x.bsd_cs_tt_id == self.bsd_cs_tt_id).ids or []
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
    bsd_td_tt_id = fields.Many2one('bsd.dat_coc.td_tt', string="Thay đổi thông tin")
    bsd_loai = fields.Selection([('bao_gia', 'Bảng tính giá'),
                                 ('td_tt', 'Thay đổi thông tin'),
                                 ('td_tt_pttt', 'Phương thức thanh toán')])
    bsd_ck_ch_ids = fields.Many2many('bsd.chiet_khau', relation="chung_rel", string="Chiết khấu chung")
    bsd_ck_nb_ids = fields.Many2many('bsd.chiet_khau', relation="noi_bo_rel", string="Chiết khấu nội bộ")
    bsd_ck_pttt_ids = fields.Many2many('bsd.chiet_khau', relation="pttt_rel", string="Chiết khấu theo PTTT")

    def action_xac_nhan(self):
        list_ps_ck = []
        if self.bsd_loai != 'td_tt_pttt':
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
        if self.bsd_loai == 'bao_gia':
            self.bsd_bao_gia_id.bsd_ps_ck_ids.unlink()
            self.bsd_bao_gia_id.write({
                'bsd_ps_ck_ids': list_ps_ck
            })
        else:
            self.bsd_td_tt_id.bsd_ps_ck_moi_ids.unlink()
            self.bsd_td_tt_id.write({
                'bsd_ps_ck_moi_ids': list_ps_ck
            })


class BsdBaoGiaChonDKBG(models.TransientModel):
    _name = 'bsd.wizard.bao_gia.chon_dkbg'
    _description = 'Chọn điều kiện bàn giao áp dụng cho bảng tính giá'

    @api.model
    def default_get(self, fields_list):
        res = super(BsdBaoGiaChonDKBG, self).default_get(fields_list)
        if self._context.get('active_model') == 'bsd.bao_gia':
            bao_gia = self.env['bsd.bao_gia'].browse(self._context.get('active_ids', []))
            res.update({
                'bsd_bao_gia_id': bao_gia.id,
                'bsd_dot_mb_id': bao_gia.bsd_dot_mb_id.id,
                'bsd_unit_id': bao_gia.bsd_unit_id.id,
                'bsd_dk_bg_ids': [(6, 0, bao_gia.bsd_bg_ids.mapped('bsd_dk_bg_id').ids)]
            })
        elif self._context.get('active_model') == 'bsd.dat_coc.td_tt':
            td_tt = self.env['bsd.dat_coc.td_tt'].browse(self._context.get('active_ids', []))
            res.update({
                'bsd_td_tt_id': td_tt.id,
                'bsd_dot_mb_id': td_tt.bsd_dot_mb_id.id,
                'bsd_unit_id': td_tt.bsd_unit_id.id,
                'bsd_dk_bg_ids': [(6, 0, td_tt.bsd_bg_ht_ids.mapped('bsd_dk_bg_id').ids)]
            })
        return res

    @api.onchange('bsd_bao_gia_id', 'bsd_dot_mb_id', 'bsd_unit_id', 'bsd_td_tt_id')
    def _onchange_ck(self):
        res = {}
        if self.bsd_bao_gia_id:
            list_dk_bg_ids = self.bsd_dot_mb_id.bsd_dkbg_ids.filtered(
                    lambda d: d.bsd_loai_sp_id == self.bsd_bao_gia_id.bsd_unit_id.bsd_loai_sp_id or not d.bsd_loai_sp_id)
            res.update({
                'domain': {
                    'bsd_dk_bg_ids': [('id', 'in', list_dk_bg_ids.ids or [])],
                }
            })
        elif self.bsd_td_tt_id:
            list_dk_bg_ids = self.bsd_dot_mb_id.bsd_dkbg_ids.filtered(
                    lambda d: d.bsd_loai_sp_id == self.bsd_td_tt_id.bsd_unit_id.bsd_loai_sp_id or not d.bsd_loai_sp_id)
            res.update({
                'domain': {
                    'bsd_dk_bg_ids': [('id', 'in', list_dk_bg_ids.ids or [])],
                }
            })
        return res

    bsd_bao_gia_id = fields.Many2one('bsd.bao_gia', string="Bảng tính giá")
    bsd_td_tt_id = fields.Many2one('bsd.dat_coc.td_tt', string="Thay đổi TT")
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
        if self.bsd_bao_gia_id:
            self.bsd_bao_gia_id.bsd_bg_ids.unlink()
            self.bsd_bao_gia_id.write({
                'bsd_bg_ids': list_dk_bg
            })
        elif self.bsd_td_tt_id:
            self.bsd_td_tt_id.bsd_bg_moi_ids.unlink()
            self.bsd_td_tt_id.write({
                'bsd_bg_moi_ids': list_dk_bg
            })