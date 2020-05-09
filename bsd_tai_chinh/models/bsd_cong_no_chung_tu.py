# -*- coding:utf-8 -*-

from odoo import models, fields, api
from odoo.exceptions import UserError
import logging
_logger = logging.getLogger(__name__)


class BsdCongNo(models.Model):
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

    company_id = fields.Many2one('res.company', string='Công ty', default=lambda self: self.env.company)
    currency_id = fields.Many2one(related="company_id.currency_id", string="Tiền tệ", readonly=True)
    state = fields.Selection([('hoan_thanh', 'Hoàn thành'), ('huy', 'Hủy')])

    bsd_loai = fields.Selection([('pt_gctc', 'Phiếu thu - Giữ chỗ thiện chí'),
                                 ('pt_gc', 'Phiếu thu - Giữ chỗ'),
                                 ('pt_dc', 'Phiếu thu - Đặt cọc'),
                                 ('pt_dtt', 'Phiếu thu - Đợt thanh toán')], string="Phân loại",
                                help="Phân loại", required=True)

    def kiem_tra_chung_tu(self):
        if self.bsd_loai == 'pt_gctc':
            cong_no_ct = self.env['bsd.cong_no_ct'].search([('bsd_gc_tc_id', '=', self.bsd_gc_tc_id.id)])
            tien = sum(cong_no_ct.mapped('bsd_tien_pb'))
            _logger.debug(self.bsd_gc_tc_id.bsd_tien_gc)
            if self.bsd_gc_tc_id.bsd_tien_gc < tien:
                raise UserError("Không thể thực hiện thanh toán dư")
            elif self.bsd_gc_tc_id.bsd_tien_gc == tien:
                self.bsd_gc_tc_id.write({
                    'bsd_thanh_toan': 'da_tt',
                    'bsd_ngay_tt': self.bsd_ngay_pb
                })
            elif 0 < tien < self.bsd_gc_tc_id.bsd_tien_gc:
                self.bsd_gc_tc_id.write({
                    'bsd_thanh_toan': 'dang_tt',
                    'bsd_ngay_tt': self.bsd_ngay_pb
                })
        elif self.bsd_loai == 'pt_gc':
            cong_no_ct = self.env['bsd.cong_no_ct'].search([('bsd_giu_cho_id', '=', self.bsd_giu_cho_id.id)])
            tien = sum(cong_no_ct.mapped('bsd_tien_pb'))
            _logger.debug(self.bsd_giu_cho_id.bsd_tien_gc)
            if self.bsd_giu_cho_id.bsd_tien_gc < tien:
                raise UserError("Không thể thực hiện thanh toán dư")
            elif self.bsd_giu_cho_id.bsd_tien_gc == tien:
                self.bsd_giu_cho_id.write({
                    'bsd_thanh_toan': 'da_tt',
                    'bsd_ngay_tt': self.bsd_ngay_pb
                })
            elif 0 < tien < self.bsd_giu_cho_id.bsd_tien_gc:
                self.bsd_giu_cho_id.write({
                    'bsd_thanh_toan': 'dang_tt',
                    'bsd_ngay_tt': self.bsd_ngay_pb
                })
        elif self.bsd_loai == 'pt_dc':
            cong_no_ct = self.env['bsd.cong_no_ct'].search([('bsd_dat_coc_id', '=', self.bsd_dat_coc_id.id)])
            tien = sum(cong_no_ct.mapped('bsd_tien_pb'))
            _logger.debug(self.bsd_dat_coc_id.bsd_tien_dc)
            if self.bsd_dat_coc_id.bsd_tien_dc < tien:
                raise UserError("Không thể thực hiện thanh toán dư")
            elif self.bsd_dat_coc_id.bsd_tien_dc == tien:
                self.bsd_dat_coc_id.write({
                    'bsd_thanh_toan': 'da_tt',
                    'bsd_ngay_tt': self.bsd_ngay_pb
                })
            elif 0 < tien < self.bsd_dat_coc_id.bsd_tien_dc:
                self.bsd_dat_coc_id.write({
                    'bsd_thanh_toan': 'dang_tt',
                    'bsd_ngay_tt': self.bsd_ngay_pb
                })
        elif self.bsd_loai == 'pt_dtt':
            cong_no_ct = self.env['bsd.cong_no_ct'].search([('bsd_dot_tt_id', '=', self.bsd_dot_tt_id.id)])
            tien = sum(cong_no_ct.mapped('bsd_tien_pb'))
            _logger.debug("Đợt thanh toán")
            _logger.debug(self.bsd_dot_tt_id.bsd_tien_dot_tt)
            if self.bsd_dot_tt_id.bsd_tien_dot_tt < tien:
                raise UserError("Không thể thực hiện thanh toán dư")
            elif self.bsd_dot_tt_id.bsd_tien_dot_tt == tien:
                self.bsd_dot_tt_id.write({
                    'bsd_thanh_toan': 'da_tt',
                    'bsd_ngay_tt': self.bsd_ngay_pb
                })
            elif 0 < tien < self.bsd_dot_tt_id.bsd_tien_dot_tt:
                self.bsd_dot_tt_id.write({
                    'bsd_thanh_toan': 'dang_tt',
                    'bsd_ngay_tt': self.bsd_ngay_pb
                })

    @api.model
    def create(self,vals):
        rec = super(BsdCongNo, self).create(vals)
        rec.kiem_tra_chung_tu()
        return rec
