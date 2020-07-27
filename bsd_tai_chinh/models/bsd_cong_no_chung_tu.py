# -*- coding:utf-8 -*-

from odoo import models, fields, api
from odoo.exceptions import UserError
import logging
_logger = logging.getLogger(__name__)


class BsdCongNoCT(models.Model):
    _name = 'bsd.cong_no_ct'
    _description = 'Công nợ chứng từ'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _rec_name = 'bsd_khach_hang_id'

    bsd_ngay_pb = fields.Datetime(string="Ngày", help="Ngày phân bổ")
    bsd_khach_hang_id = fields.Many2one('res.partner', string="Khách hàng", help="Khách hàng")
    bsd_tien_pb = fields.Monetary(string="Tiền", help="Tiền phân bổ")

    bsd_gc_tc_id = fields.Many2one('bsd.gc_tc', string="Giữ chỗ thiện chí", help="Giữ chỗ thiện chí")
    bsd_giu_cho_id = fields.Many2one('bsd.giu_cho', string="Giữ chỗ", help="Giữ chỗ")
    bsd_dat_coc_id = fields.Many2one('bsd.dat_coc', string="Đặt cọc", help="Đặt cọc")
    bsd_hd_ban_id = fields.Many2one('bsd.hd_ban', string="Hợp đồng", help="Hợp đồng")
    bsd_dot_tt_id = fields.Many2one('bsd.lich_thanh_toan', string="Đợt thanh toán")
    bsd_phieu_thu_id = fields.Many2one('bsd.phieu_thu', string="Phiếu thu", help="Phiếu thu")
    bsd_hoan_tien_id = fields.Many2one('bsd.hoan_tien', string="Hoàn tiền", help="Hoàn tiền")
    bsd_giam_no_id = fields.Many2one('bsd.giam_no', string="Điều chỉnh giảm", help="Điều chỉnh giảm")
    company_id = fields.Many2one('res.company', string='Công ty', default=lambda self: self.env.company)
    currency_id = fields.Many2one(related="company_id.currency_id", string="Tiền tệ", readonly=True)
    state = fields.Selection([('hoan_thanh', 'Hoàn thành'), ('huy', 'Hủy')])

    bsd_loai = fields.Selection([('pt_gctc', 'Phiếu thu - Giữ chỗ thiện chí'),
                                 ('pt_gc', 'Phiếu thu - Giữ chỗ'),
                                 ('pt_dc', 'Phiếu thu - Đặt cọc'),
                                 ('pt_dtt', 'Phiếu thu - Đợt thanh toán'),
                                 ('pt_ht', 'Phiếu thu - Hoàn tiền'),
                                 ('giam_ht', 'Điều chỉnh giảm - Hoàn tiền'),
                                 ('giam_gctc', 'Điều chỉnh giảm - Giữ chỗ thiện chí'),
                                 ('giam_gc', 'Điều chỉnh giảm - Giữ chỗ')], string="Phân loại",
                                help="Phân loại", required=True)
    bsd_can_tru_id = fields.Many2one('bsd.can_tru', string="Cấn trừ", readonly=True)

    def kiem_tra_chung_tu(self):
        if self.bsd_loai == 'pt_gctc':
            cong_no_ct = self.env['bsd.cong_no_ct'].search([('bsd_gc_tc_id', '=', self.bsd_gc_tc_id.id)])
            tien = sum(cong_no_ct.mapped('bsd_tien_pb'))
            _logger.debug(self.bsd_gc_tc_id.bsd_tien_gc)
            if self.bsd_gc_tc_id.bsd_tien_gc < tien:
                raise UserError("Không thể thực hiện thanh toán dư")

        elif self.bsd_loai == 'pt_gc':
            cong_no_ct = self.env['bsd.cong_no_ct'].search([('bsd_giu_cho_id', '=', self.bsd_giu_cho_id.id)])
            tien = sum(cong_no_ct.mapped('bsd_tien_pb'))
            if self.bsd_giu_cho_id.bsd_tien_gc < tien:
                raise UserError("Không thể thực hiện thanh toán dư")
            # Kiểm tra nếu là giữ chỗ trước mở bán nếu thanh toán đủ thì chuyển trạng thái sang giữ chỗ
            if self.bsd_giu_cho_id.bsd_truoc_mb and not self.bsd_giu_cho_id.bsd_gc_da:
                if self.bsd_giu_cho_id.bsd_tien_gc == tien:
                    self.bsd_giu_cho_id.write({
                        'state': 'giu_cho',
                    })
                    # Tính lại hạn báo giá
                    self.bsd_giu_cho_id.tinh_lai_hbg()
                    if self.bsd_giu_cho_id.bsd_unit_id.state == 'dat_cho':
                        self.bsd_giu_cho_id.bsd_unit_id.write({
                            'state': 'giu_cho',
                        })

        elif self.bsd_loai == 'pt_dc':
            cong_no_ct = self.env['bsd.cong_no_ct'].search([('bsd_dat_coc_id', '=', self.bsd_dat_coc_id.id),
                                                            ('bsd_dot_tt_id', '=', False)])
            tien = sum(cong_no_ct.mapped('bsd_tien_pb'))
            if self.bsd_dat_coc_id.bsd_tien_dc < tien:
                raise UserError("Không thể thực hiện thanh toán dư")
            if self.bsd_dat_coc_id.bsd_tien_dc == tien:
                self.bsd_dat_coc_id.write({
                    'state': 'dat_coc',
                })

        elif self.bsd_loai == 'pt_dtt':
            cong_no_ct = self.env['bsd.cong_no_ct'].search([('bsd_dot_tt_id', '=', self.bsd_dot_tt_id.id)])
            tien = sum(cong_no_ct.mapped('bsd_tien_pb'))
            if self.bsd_dot_tt_id.bsd_tien_dot_tt < tien:
                raise UserError("Không thể thực hiện thanh toán dư")

            hd_ban = self.bsd_dot_tt_id.bsd_hd_ban_id
            # Kiểm tra điều kiện đợt tt tạo giao dịch chiết khấu và khuyến mãi
            if hd_ban:
                # Gọi hàm xử lý giao dịch chiết khấu thanh toán trước hạn
                self.bsd_dot_tt_id.tao_ck_ttth(ngay_tt=self.bsd_ngay_pb, tien_tt=self.bsd_tien_pb)
                # Gọi hàm xử lý giao dịch chiết khấu thanh toán nhanh
                self.bsd_dot_tt_id.tao_ck_ttn()
                # Gọi hàm xứ lý khuyến mãi
                hd_ban.tao_giao_dich_khuyen_mai(ngay_tt=self.bsd_ngay_pb)
            # Cập nhật trạng thái hợp đồng khi thanh toán đủ đợt thanh toán
            if self.bsd_dot_tt_id.bsd_tien_dot_tt == tien:
                # Gọi hàm xử lý khi thanh toán đợt 1 cho hợp đồng
                if self.bsd_dot_tt_id.bsd_stt == 1:
                    hd_ban.action_tt_dot1()
                # Gọi hàm xử lý khi thanh toán đợt đủ điều kiện làm hợp đồng
                if self.bsd_dot_tt_id.bsd_dot_ky_hd:
                    hd_ban.action_du_dk()
                # Gọi hàm xử lý khi thanh toán đợt sau khi ký hợp đồng
                if hd_ban.state == 'da_ky':
                    hd_ban.action_dang_tt()
                # Gọi hàm xử lý khi thanh toám đợt dự kiến bàn giao
                if hd_ban.state in ['da_ky', 'dang_tt']:
                    hd_ban.action_du_dkbg()
        elif self.bsd_loai == 'pt_ht':
            cong_no_ct = self.env['bsd.cong_no_ct'].search([('bsd_phieu_thu_id', '=', self.bsd_phieu_thu_id.id)])
            tien = sum(cong_no_ct.mapped('bsd_tien_pb'))
            if self.bsd_phieu_thu_id.bsd_tien < tien:
                raise UserError("Không thể thực hiện thanh toán dư")

    @api.model
    def create(self, vals):
        rec = super(BsdCongNoCT, self).create(vals)
        rec.kiem_tra_chung_tu()
        return rec
