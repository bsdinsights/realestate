# -*- coding:utf-8 -*-

from odoo import models, fields, api
from odoo.exceptions import UserError
import datetime
import logging
_logger = logging.getLogger(__name__)


class BsdBaoGiaLTT(models.Model):
    _inherit = 'bsd.lich_thanh_toan'

    bsd_tien_da_tt = fields.Monetary(string="Đã thanh toán", help="Đã thanh toán",
                                     compute="_compute_tien_tt", store=True)
    bsd_tien_phai_tt = fields.Monetary(string="Phải thanh toán", help="Đã thanh toán",
                                       compute="_compute_tien_tt", store=True)
    bsd_ct_ids = fields.One2many('bsd.cong_no_ct', 'bsd_dot_tt_id', string="Công nợ chứng tự",
                                 domain=[('bsd_loai', '=', 'pt_dtt')], readonly=True)
    bsd_ngay_tt = fields.Datetime(compute='_compute_tien_tt', store=True)
    bsd_thanh_toan = fields.Selection(compute='_compute_tien_tt', store=True)

    @api.depends('bsd_ct_ids', 'bsd_ct_ids.bsd_tien_pb', 'bsd_tien_dot_tt')
    def _compute_tien_tt(self):
        for each in self:
            each.bsd_tien_da_tt = sum(each.bsd_ct_ids.mapped('bsd_tien_pb'))
            each.bsd_tien_phai_tt = each.bsd_tien_dot_tt - each.bsd_tien_da_tt - each.bsd_tien_dc

            if each.bsd_tien_phai_tt == 0:
                each.bsd_thanh_toan = 'da_tt'
            elif 0 < each.bsd_tien_phai_tt < each.bsd_tien_dot_tt:
                each.bsd_thanh_toan = 'dang_tt'
            else:
                each.bsd_thanh_toan = 'chua_tt'

            if each.bsd_ct_ids:
                each.bsd_ngay_tt = max(each.bsd_ct_ids.mapped('bsd_ngay_pb'))
            else:
                each.bsd_ngay_tt = None

    # DV.01.09 Theo dõi chiết khấu thanh toán trước hạn
    def tao_ck_ttth(self, ngay_tt, tien_tt):
        # Kiểm tra trạng thái của hợp đồng đã ký hoặc đang thanh toán
        if self.bsd_hd_ban_id.state not in ['da_ky', 'dang_tt']:
            return
        # Lấy thông tin đợt mở bán của hợp đồng
        dot_mb = self.bsd_hd_ban_id.bsd_dot_mb_id
        # Kiểm tra hợp đồng có đọt mở bán có áp dụng chiết khấu trước hạn hay không
        if not dot_mb.bsd_ck_ttth_id:
            return
        if not self.bsd_ngay_hh_tt:
            return
        # Kiểm tra ngày thanh toán có trước ngày hết hạn hay không
        if ngay_tt.date() >= self.bsd_ngay_hh_tt:
            return
        # Lấy Item chiết khấu thanh toán trước hạn
        ck_ttth = dot_mb.bsd_ck_ttth_id.bsd_ct_ids.filtered(lambda c: c.bsd_tu_ngay <= ngay_tt.date() <= c.bsd_den_ngay)
        if not ck_ttth:
            return
        if len(ck_ttth) > 1:
            raise UserError("Tìm thấy nhiều hơn 1 chiết khấu. Vui lòng kiểm tra lại")
        so_ngay_th = (self.bsd_ngay_hh_tt - ngay_tt.date()).days
        if ck_ttth.bsd_chiet_khau_id.bsd_cach_tinh == 'tien':
            tien_ck = so_ngay_th * ck_ttth.bsd_chiet_khau_id.bsd_tien_ck
        else:
            tien_ck = ((ck_ttth.bsd_chiet_khau_id.bsd_tl_ck/100) * so_ngay_th) * tien_tt
        # Tạo Giao dich chiết khấu
        self.env['bsd.ps_gd_ck'].create({
            'bsd_ma_ck': ck_ttth.bsd_chiet_khau_id.bsd_ma_ck,
            'bsd_ten_ck': ck_ttth.bsd_chiet_khau_id.bsd_ten_ck,
            'bsd_dat_coc_id': self.bsd_dat_coc_id.id,
            'bsd_hd_ban_id': self.bsd_hd_ban_id.id,
            'bsd_unit_id': self.bsd_hd_ban_id.bsd_unit_id.id,
            'bsd_loai_ck': 'ttth',
            'bsd_ltt_id': self.id,
            'bsd_sn_th': so_ngay_th,
            'bsd_tien_dot_tt': tien_tt,
            'bsd_tl_ck': ck_ttth.bsd_chiet_khau_id.bsd_tl_ck,
            'bsd_tien': ck_ttth.bsd_chiet_khau_id.bsd_tien_ck,
            'bsd_tien_ck': tien_ck,
        })

    # DV.01.09 Theo dõi chiết khấu thanh toán nhanh
    def tao_ck_ttn(self):
        # Kiểm tra trạng thái của hợp đồng
        if self.bsd_hd_ban_id.state not in ['da_ky', 'dang_tt']:
            return
        # Lấy thông tin đợt mở bán của hợp đồng
        dot_mb = self.bsd_hd_ban_id.bsd_dot_mb_id
        # Kiểm tra xem đã hưởng chiết khấu thanh toán nhanh chưa
        if self.bsd_hd_ban_id.bsd_dh_ck_ttn:
            return
        # Kiểm tra hợp đồng có đọt mở bán có áp dụng chiết khấu nhanh hay không
        if not dot_mb.bsd_ck_ttn_id:
            return
        # Lấy Item chiết khấu thanh toán nhanh
        ck_ttn = dot_mb.bsd_ck_ttn_id.bsd_ct_ids.\
            filtered(lambda c: c.bsd_tu_ngay <= self.bsd_ngay_tt.date() <= c.bsd_den_ngay)
        if not ck_ttn:
            return
        if len(ck_ttn) > 1:
            raise UserError("Tìm thấy nhiều hơn 1 chiết khấu. Vui lòng kiểm tra lại")
        # Kiểm tra tỷ lệ thanh toán của hợp đồng
        if self.bsd_hd_ban_id.bsd_tl_tt_hd < ck_ttn.bsd_chiet_khau_id.bsd_tl_tt:
            return
        if ck_ttn.bsd_chiet_khau_id.bsd_cach_tinh == 'tien':
            tien_ck = ck_ttn.bsd_chiet_khau_id.bsd_tien_ck
        else:
            tien_ck = ck_ttn.bsd_chiet_khau_id.bsd_tl_ck / 100 * self.bsd_hd_ban_id.bsd_gia_truoc_thue
        # Tạo Giao dich chiết khấu
        _logger.debug(self.bsd_ngay_tt.date())
        _logger.debug(ck_ttn)
        _logger.debug(ck_ttn.bsd_chiet_khau_id.bsd_ma_ck)
        self.env['bsd.ps_gd_ck'].create({
            'bsd_ma_ck': ck_ttn.bsd_chiet_khau_id.bsd_ma_ck,
            'bsd_ten_ck': ck_ttn.bsd_chiet_khau_id.bsd_ten_ck,
            'bsd_dat_coc_id': self.bsd_dat_coc_id.id,
            'bsd_hd_ban_id': self.bsd_hd_ban_id.id,
            'bsd_unit_id': self.bsd_hd_ban_id.bsd_unit_id.id,
            'bsd_loai_ck': 'ttn',
            'bsd_tl_ck': ck_ttn.bsd_chiet_khau_id.bsd_tl_ck,
            'bsd_tien': ck_ttn.bsd_chiet_khau_id.bsd_tien_ck,
            'bsd_tien_ck': tien_ck,
        })
        self.bsd_hd_ban_id.write({
            'bsd_dh_ck_ttn': True
        })
