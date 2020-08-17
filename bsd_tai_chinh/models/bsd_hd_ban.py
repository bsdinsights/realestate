# -*- coding:utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError
import logging
_logger = logging.getLogger(__name__)


class BsdHdBan(models.Model):
    _inherit = 'bsd.hd_ban'

    bsd_tl_tt_hd = fields.Float(string="Tỷ lệ thanh toán HĐ", help="Tỷ lệ thanh toán hợp đồng", compute='_compute_tl_tt',
                                store=True, digits=(10, 1))
    bsd_tien_tt_hd = fields.Monetary(string="Tiền thanh toán HĐ", help="Tiền thanh toán hợp đồng",
                                     compute='_compute_tl_tt', store=True)

    bsd_phi_ps_ids = fields.One2many('bsd.phi_ps', 'bsd_hd_ban_id', string="Danh sách phí phát sinh", readonly=True)

    @api.depends('bsd_ltt_ids.bsd_tien_da_tt', 'bsd_tong_gia')
    def _compute_tl_tt(self):
        for each in self:
            if each.bsd_tong_gia > 0:
                each.bsd_tien_tt_hd = sum(each.bsd_ltt_ids.mapped('bsd_tien_da_tt')) + \
                                      each.bsd_ltt_ids.filtered(lambda x: x.bsd_stt == 1).bsd_tien_dc
                each.bsd_tl_tt_hd = each.bsd_tien_tt_hd / (each.bsd_tong_gia - each.bsd_tien_pbt) * 100

    # DV.01.13 Theo dõi giao dịch khuyến mãi
    def tao_giao_dich_khuyen_mai(self, ngay_tt):
        ngay_tt = ngay_tt.date()
        _logger.debug("tạo giao dịch chiết khấu")
        # Các khuyến mãi có điều kiện của hợp đồng
        km_hd = self.bsd_dot_mb_id.bsd_km_ids\
            .filtered(lambda k: k.bsd_loai != 'khong')
        _logger.debug(km_hd)
        # Kiểm tra khuyến mãi của hợp đồng đã tạo khuyến mãi
        km_da_ps_gd = self.env['bsd.ps_gd_km'].search([('bsd_hd_ban_id', '=', self.id)]).mapped('bsd_khuyen_mai_id')
        _logger.debug(km_da_ps_gd)
        # Các khuyến mãi chưa tạo giao dịch
        km_ids = km_hd - km_da_ps_gd
        _logger.debug(km_ids)
        # Kiểm tra thời điểm thanh toán nằm trong khuyến mãi
        km_ids = km_ids.filtered(lambda k: k.bsd_tu_ngay <= ngay_tt <= k.bsd_den_ngay)
        # Lấy ngày thanh toán đặc cọc
        ngay_tt_dc = self.bsd_dat_coc_id.bsd_ngay_tt.date()
        _logger.debug(ngay_tt_dc)
        for km_check_dc in km_ids.filtered(lambda k: k.bsd_ngay_hldc):
            # Kiểm tra ngày thanh toán đặc cọc
            if ngay_tt_dc > km_check_dc.bsd_ngay_hldc:
                continue
            if km_check_dc.bsd_loai == 'tien':
                if self.bsd_tien_tt_hd < km_check_dc.bsd_tong_tt:
                    continue
            if km_check_dc.bsd_loai == 'ty_le':
                if self.bsd_tl_tt_hd < km_check_dc.bsd_tl_tt:
                    continue
            if km_check_dc.bsd_loai == 'ty_le_tien':
                if self.bsd_tien_tt_hd < km_check_dc.bsd_tong_tt and self.bsd_tl_tt_hd < km_check_dc.bsd_tl_tt:
                    continue
            self.env['bsd.ps_gd_km'].create({
                'bsd_khuyen_mai_id': km_check_dc.id,
                'bsd_hd_ban_id': self.id,
                'bsd_khach_hang_id': self.bsd_khach_hang_id.id,
                'bsd_ngay_tt': ngay_tt,
                'state': 'xac_nhan',
            })
        for km in km_ids.filtered(lambda k: not k.bsd_ngay_hldc):
            if km.bsd_loai == 'tien':
                if self.bsd_tien_tt_hd < km.bsd_tong_tt:
                    continue
            if km.bsd_loai == 'ty_le':
                if self.bsd_tl_tt_hd < km.bsd_tl_tt:
                    continue
            if km.bsd_loai == 'ty_le_tien':
                if self.bsd_tien_tt_hd < km.bsd_tong_tt and self.bsd_tl_tt_hd < km.bsd_tl_tt:
                    continue
            self.env['bsd.ps_gd_km'].create({
                'bsd_khuyen_mai_id': km.id,
                'bsd_hd_ban_id': self.id,
                'bsd_khach_hang_id': self.bsd_khach_hang_id.id,
                'bsd_ngay_tt': ngay_tt,
                'state': 'xac_nhan',
            })

    # DV.01.15 - Cập nhật trạng thái Thanh toán đợt 1
    def action_tt_dot1(self):
        _logger.debug("Cập nhật đợt thanh toán 1")
        if self.state == 'ht_dc' and not self.bsd_duyet_db:
            self.write({
                'state': 'tt_dot1'
            })

    # DV.01.16 - Cập nhật trạng thái Đủ điều kiện
    def action_du_dk(self):
        # Kiểm tra nếu hợp đồng có duyệt đặc biệt thì ko cập nhật trạng thái đủ dk
        if self.bsd_duyet_db:
            return
        if self.bsd_co_ttdc:
            if self.state != 'da_ky_ttdc':
                raise UserError("Hợp đồng chưa thực hiện ký thỏa thuận đặt cọc")
            else:
                self.write({
                    'state': 'du_dk'
                })
        else:
            if self.state == 'tt_dot1':
                self.write({
                    'state': 'du_dk'
                })

    # DV.01.21 Cập nhật trạng thái Đang thanh toán
    def action_dang_tt(self):
        # Kiểm tra nếu hợp đồng có duyệt bàn giao đặc biệt thì không cập nhật trạng thái hợp đồng
        if self.bsd_duyet_bgdb:
            return
        # Lấy đợt thanh toán ký hợp đồng
        dot_ky_hd = self.bsd_ltt_ids.filtered(lambda l: l.bsd_dot_ky_hd)
        stt_dot_ky_hd = dot_ky_hd.bsd_stt
        dot_sau_ky_hd = self.bsd_ltt_ids.filtered(lambda l: l.bsd_stt == stt_dot_ky_hd + 1)
        # Lấy đợt thanh toán sau ký hợp đồng
        if dot_sau_ky_hd.bsd_thanh_toan == 'da_tt':
            self.write({
                'state': 'dang_tt'
            })

    # DV.01.22 Cập nhật trạng thái đủ điều kiện bàn giao
    def action_du_dkbg(self):
        # Kiểm tra nếu hợp đồng có duyệt bàn giao đặt biệt thì không cập nhật trạng thái hợp đồng
        if self.bsd_duyet_bgdb:
            return
        # Kiểm tra hợp đông đã được thanh toán phí bảo trì
        if not self.bsd_dot_pbt_ids:
            raise UserError(_('Hợp đồng chưa ghi nhận thu phí bảo trì'))
        if len(self.bsd_dot_pbt_ids) > 1:
            raise UserError(_('Hợp đồng có nhiều hơn 1 đợt thu phí bảo trì'))
        if self.bsd_dot_pbt_ids.bsd_thanh_toan != 'da_tt':
            return
        # Kiểm tra hợp đông đã được thanh toán phí quản lý
        if not self.bsd_dot_pql_ids:
            raise UserError(_('Hợp đồng chưa ghi nhận thu phí quản lý'))
        if len(self.bsd_dot_pql_ids) > 1:
            raise UserError(_('Hợp đồng có nhiều hơn 1 đợt thu phí quản lý'))
        if self.bsd_dot_pql_ids.bsd_thanh_toan != 'da_tt':
            return
        # Kiểm tra hợp đồng đã thanh toán đợt dự kiến bàn giao
        dot_dkbg = self.bsd_ltt_ids.filtered(lambda l: l.bsd_ma_dtt == 'DKBG')
        if not dot_dkbg:
            raise UserError(_("Hợp đồng không có đợt dự kiến bàn giao"))
        if len(dot_dkbg) > 1:
            raise UserError(_("Hợp đồng có nhiều hơn 1 đợt dkbg"))
        if dot_dkbg.bsd_thanh_toan != 'da_tt':
            return
        # Kiểm tra các phí phát sinh từ đợt dkbg trở về trước
        dot_pps = self.bsd_ltt_ids.filtered(lambda d: d.bsd_stt <= dot_dkbg.bsd_stt)
        # Lấy các phí phát sinh
        phi_ps_ids = self.env['bsd.phi_ps'].search([('bsd_hd_ban_id', '=', self.id),
                                                    ('bsd_dot_tt_id', 'in', dot_pps.ids),
                                                    ('state', '=', 'ghi_so')])
        phi_ps_ids = phi_ps_ids.filtered(lambda p: p.bsd_thanh_toan != 'da_tt')
        if phi_ps_ids:
            return
        # Kiểm tra tỷ lệ thanh toán của hợp đồng với điều kiện bàn giao trên sản phẩm
        if self.bsd_tl_tt_hd < self.bsd_unit_id.bsd_dk_bg:
            return
        # Ghi nhận trạng thái đủ dk bàn giao
        self.write({
            'state': 'du_dkbg'
        })
        # Cập nhật trạng thái unit
        self.bsd_unit_id.write({
            'state': 'du_dkbg'
        })

    # DV.01.23 Cập nhật trạng thái hoàn tất thanh toán
    def action_ht_tt(self):
        # Kiểm tra đã thu đủ nợ gốc chưa
        if self.bsd_ltt_ids.filtered(lambda l: l.bsd_thanh_toan != 'da_tt'):
            return
        # Kiểm tra đã thu phí bảo trì chưa
        if self.bsd_dot_pbt_ids.filtered(lambda p: p.bsd_thanh_toan != 'da_tt'):
            return
        # Kiểm tra đã thu phí quản lý chưa
        if self.bsd_dot_pql_ids.filtered(lambda p: p.bsd_thanh_toan != 'da_tt'):
            return
        # Kiểm tra đã thu đủ phí phát sinh chưa
        if self.bsd_phi_ps_ids.filtered(lambda p: p.bsd_thanh_toan != 'da_tt'):
            return
        # Cập nhật trạng thái hoàn tất thanh toán
        self.write({
            'state': 'ht_tt'
        })
        # Cập nhật trạng thái hoàn tất thanh toán cho sản phẩm
        self.bsd_unit_id.write({
            'state': 'ht_tt'
        })
