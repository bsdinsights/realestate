# -*- coding:utf-8 -*-

from odoo import models, fields, api
from odoo.exceptions import UserError
from odoo.tools import float_utils
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
    bsd_phieu_thu_id = fields.Many2one('bsd.phieu_thu', string="Phiếu thanh toán", help="Phiếu thanh toán")
    bsd_hoan_tien_id = fields.Many2one('bsd.hoan_tien', string="Hoàn tiền", help="Hoàn tiền")
    bsd_phi_ps_id = fields.Many2one('bsd.phi_ps', string="Phí phát sinh", help="Phí phát sinh")
    bsd_thanh_ly_id = fields.Many2one('bsd.thanh_ly', string="Thanh lý", help="Thanh lý")
    bsd_lai_phat_id = fields.Many2one('bsd.lai_phat', string="Lãi phạt", help="Lãi phạt")
    company_id = fields.Many2one('res.company', string='Công ty', default=lambda self: self.env.company)
    currency_id = fields.Many2one(related="company_id.currency_id", string="Tiền tệ", readonly=True)
    state = fields.Selection([('hieu_luc', 'Hiệu lực'), ('huy', 'Hủy')],
                             string="Tình trạng",
                             default='hieu_luc', required=True, readonly=True, tracking=1)

    bsd_loai = fields.Selection([('pt_gctc', 'Phiếu thanh toán - Giữ chỗ thiện chí'),
                                 ('pt_gc', 'Phiếu thanh toán - Giữ chỗ'),
                                 ('pt_dc', 'Phiếu thanh toán - Đặt cọc'),
                                 ('pt_dtt', 'Phiếu thanh toán - Đợt thanh toán'),
                                 ('pt_ht', 'Phiếu thanh toán - Hoàn tiền'),
                                 ('pt_pps', 'Phiếu thanh toán - Phí phát sinh')], string="Phân loại",
                                help="Phân loại", required=True)
    bsd_can_tru_id = fields.Many2one('bsd.can_tru', string="Cấn trừ", readonly=True)

    def kiem_tra_chung_tu(self):
        if self.bsd_loai == 'pt_gctc':
            cong_no_ct = self.env['bsd.cong_no_ct'].search([('bsd_gc_tc_id', '=', self.bsd_gc_tc_id.id)])
            tien = sum(cong_no_ct.mapped('bsd_tien_pb'))
            _logger.debug(self.bsd_gc_tc_id.bsd_tien_gc)
            if self.bsd_gc_tc_id.bsd_tien_gc < tien:
                raise UserError("Không thể thực hiện thanh toán dư.")
            elif self.bsd_gc_tc_id.bsd_tien_gc == tien:
                gc_th_rap_can = self.env['bsd.gc_tc'].search([('bsd_du_an_id', '=', self.bsd_gc_tc_id.bsd_du_an_id.id),
                                                              ('state', '=', 'giu_cho')])
                if gc_th_rap_can:
                    self.bsd_gc_tc_id.write({
                        'state': 'cho_rc',
                    })
                else:
                    self.bsd_gc_tc_id.write({
                        'state': 'giu_cho',
                    })
                # Sinh số thứ tự cho giữ chỗ thiện chí sau khi thanh toán
                self.bsd_gc_tc_id.create_stt()

        elif self.bsd_loai == 'pt_gc':
            cong_no_ct = self.env['bsd.cong_no_ct'].search([('bsd_giu_cho_id', '=', self.bsd_giu_cho_id.id)])
            tien = sum(cong_no_ct.mapped('bsd_tien_pb'))
            if self.bsd_giu_cho_id.bsd_tien_gc < tien:
                raise UserError("Không thể thực hiện thanh toán dư.")
            # Kiểm tra nếu là giữ chỗ trước mở bán nếu thanh toán đủ thì chuyển trạng thái sang giữ chỗ
            if self.bsd_giu_cho_id.bsd_truoc_mb and not self.bsd_giu_cho_id.bsd_gc_da:
                if self.bsd_giu_cho_id.bsd_tien_gc == tien:
                    # Tính lại hạn báo giá
                    # Chuyển trạng thái của giữ chỗ
                    self.bsd_giu_cho_id.tinh_lai_hbg()
                    if self.bsd_giu_cho_id.bsd_unit_id.state == 'dat_cho':
                        self.bsd_giu_cho_id.bsd_unit_id.write({
                            'state': 'giu_cho',
                        })

        elif self.bsd_loai == 'pt_dc':
            cong_no_ct = self.env['bsd.cong_no_ct'].search([('bsd_dat_coc_id', '=', self.bsd_dat_coc_id.id),
                                                            ('bsd_dot_tt_id', '=', False)])
            tien = sum(cong_no_ct.mapped('bsd_tien_pb')) + self.bsd_dat_coc_id.bsd_tien_gc
            if self.bsd_dat_coc_id.bsd_tien_dc < tien:
                raise UserError("Không thể thực hiện thanh toán dư.")
            if self.bsd_dat_coc_id.bsd_tien_dc == tien:
                self.bsd_dat_coc_id.cap_nhat_trang_thai()

        elif self.bsd_loai == 'pt_dtt':
            # Kiểm tra đợt thanh toán đã có hạn thanh toán chưa
            if not self.bsd_dot_tt_id.bsd_ngay_hh_tt:
                raise UserError('Đợt thanh toán chưa có hạn thanh toán.\nVui lòng kiểm tra lại thông tin.')
            cong_no_ct = self.env['bsd.cong_no_ct'].search([('bsd_dot_tt_id', '=', self.bsd_dot_tt_id.id)])
            tien = sum(cong_no_ct.mapped('bsd_tien_pb'))
            if self.bsd_dot_tt_id.bsd_tien_dot_tt < tien:
                raise UserError("Không thể thực hiện thanh toán dư.")

            hd_ban = self.bsd_dot_tt_id.bsd_hd_ban_id
            # Kiểm tra điều kiện đợt tt tạo giao dịch chiết khấu và khuyến mãi
            if hd_ban:
                # Gọi hàm xử lý giao dịch chiết khấu thanh toán trước hạn
                self.bsd_dot_tt_id.tao_ck_ttth(ngay_tt=self.bsd_ngay_pb, tien_tt=self.bsd_tien_pb)
                # Gọi hàm xử lý giao dịch chiết khấu thanh toán nhanh
                self.bsd_dot_tt_id.tao_ck_ttn()
                # Gọi hàm xứ lý khuyến mãi
                hd_ban.tao_giao_dich_khuyen_mai(ngay_tt=self.bsd_ngay_pb)
                # Gọi hàm xử lý lãi phạt chậm thanh toán
                self.bsd_dot_tt_id.tao_lp_tt(ngay_tt=self.bsd_ngay_pb, tien_tt=self.bsd_tien_pb,
                                             thanh_toan=self.bsd_phieu_thu_id)
            # Cập nhật trạng thái hợp đồng khi thanh toán đủ đợt thanh toán
            tien_thu_dot = self.bsd_dot_tt_id.bsd_tien_dot_tt - self.bsd_dot_tt_id.bsd_tien_dc
            if float_utils.float_compare(tien_thu_dot, tien, 4) == 0:
                # Gọi hàm xử lý khi thanh toán đợt 1 cho hợp đồng
                _logger.debug("thanh toán đủ")
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
                # Gọi hàm kiểm tra đã hoàn tất thanh toán hợp đồng
                hd_ban.action_ht_tt()

        elif self.bsd_loai == 'pt_ht':
            cong_no_ct = self.env['bsd.cong_no_ct'].search([('bsd_phieu_thu_id', '=', self.bsd_phieu_thu_id.id)])
            tien = sum(cong_no_ct.mapped('bsd_tien_pb'))
            if self.bsd_phieu_thu_id.bsd_tien < tien:
                raise UserError("Không thể thực hiện thanh toán dư.")

        elif self.bsd_loai == 'pt_pps':
            cong_no_ct = self.env['bsd.cong_no_ct'].search([('bsd_phi_ps_id', '=', self.bsd_phi_ps_id.id)])
            tien = sum(cong_no_ct.mapped('bsd_tien_pb'))
            if self.bsd_phi_ps_id.bsd_tong_tien < tien:
                raise UserError("Không thể thực hiện thanh toán dư.")
            self.bsd_phi_ps_id.bsd_hd_ban_id.action_du_dkbg()

    @api.model
    def create(self, vals):
        rec = super(BsdCongNoCT, self).create(vals)
        rec.kiem_tra_chung_tu()
        return rec
