# -*- coding:utf-8 -*-

from odoo import models, fields, api
from odoo.exceptions import UserError
import logging
_logger = logging.getLogger(__name__)


class BsdCanTru(models.Model):
    _name = 'bsd.can_tru'
    _description = 'Cấn trừ công nợ khách hàng'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _rec_name = 'bsd_ma_kh'

    company_id = fields.Many2one('res.company', string='Công ty', default=lambda self: self.env.company)
    currency_id = fields.Many2one(related="company_id.currency_id", string="Tiền tệ", readonly=True)
    bsd_ma_kh = fields.Char(string="Mã khách hàng", help="Mã khách hàng", required=True)
    bsd_khach_hang_id = fields.Many2one("res.partner", string="Tên khách hàng", help="Tên khách hàng", required=True)
    bsd_ngay_can_tru = fields.Datetime(string="Ngày cấn trừ", help="Ngày cấn trừ", required=True,
                                       default=lambda self: fields.Datetime.now())
    bsd_tien_can_tru = fields.Monetary(string="Tiền cấn trừ", compute='_compute_tien_can_tru', store=True)
    bsd_loai_ct = fields.Selection([('phieu_thu', 'Phiếu thu')], string="Loại chứng từ", help="Loại chứng từ",
                                   required=True)
    bsd_phieu_thu_id = fields.Many2one('bsd.phieu_thu', string="Phiếu thu", help="Phiếu thu")
    bsd_ngay_ct = fields.Datetime(string="Ngày chứng từ", help="Ngày chứng từ", related='bsd_phieu_thu_id.bsd_ngay_pt')
    bsd_tien_con_lai = fields.Monetary(related="bsd_phieu_thu_id.bsd_tien_con_lai", store=True)
    state = fields.Selection([('nhap', 'Nháp'),
                              ('can_tru', 'Cấn trừ'),
                              ('huy_ct', 'Hủy cấn trừ')], string="Trạng thái", requried=True, tracking=1,
                             default='nhap', readonly=True)
    bsd_ct_ids = fields.One2many('bsd.can_tru_ct', 'bsd_can_tru_id', string="Chi tiết")

    # TC.04.02 So sánh tiền cấn trừ và tiền còn lại
    @api.constrains('bsd_tien_can_tru')
    def _constrains_tien_can_tru(self):
        if self.bsd_tien_can_tru > self.bsd_tien_con_lai:
            raise UserError("Tiền cấn trừ không thể lớn hơn tiền còn lại")

    @api.depends('bsd_ct_ids', 'bsd_ct_ids.bsd_tien_can_tru')
    def _compute_tien_can_tru(self):
        for each in self:
            each.bsd_tien_can_tru = sum(each.bsd_ct_ids.mapped('bsd_tien_can_tru'))

    # TC.04.01 Load chứng từ cần cấn trừ
    def action_load(self):
        # Xóa bảng chi tiết
        self.bsd_ct_ids.unlink()
        # Lấy chứng từ giữ chỗ thiện chí
        gc_tc_ids = self.env['bsd.gc_tc'].search([('bsd_khach_hang_id', '=', self.bsd_khach_hang_id.id),
                                                  ('state', '!=', 'nhap'),
                                                  ('bsd_thanh_toan', '!=', 'da_tt')])
        for gc_tc in gc_tc_ids:
            self.bsd_ct_ids.create({
                'bsd_gc_tc_id': gc_tc.id,
                'bsd_so_ct': gc_tc.bsd_ma_gctc,
                'bsd_loai_ct': 'pt_gctc',
                'bsd_tien': gc_tc.bsd_tien_gc,
                'bsd_tien_phai_tt': gc_tc.bsd_tien_phai_tt,
                'bsd_can_tru_id': self.id,
            })
        # Lấy chứng từ giữ chỗ
        giu_cho_ids = self.env['bsd.giu_cho'].search([('bsd_khach_hang_id', '=', self.bsd_khach_hang_id.id),
                                                      ('state', '!=', 'nhap'),
                                                      ('bsd_thanh_toan', '!=', 'da_tt')])
        for giu_cho in giu_cho_ids:
            self.bsd_ct_ids.create({
                'bsd_giu_cho_id': giu_cho.id,
                'bsd_so_ct': giu_cho.bsd_ma_gc,
                'bsd_loai_ct': 'pt_gc',
                'bsd_tien': giu_cho.bsd_tien_gc,
                'bsd_tien_phai_tt': giu_cho.bsd_tien_phai_tt,
                'bsd_can_tru_id': self.id,
            })

        # Lấy chứng từ giữ chỗ
        dat_coc_ids = self.env['bsd.dat_coc'].search([('bsd_khach_hang_id', '=', self.bsd_khach_hang_id.id),
                                                      ('state', '!=', 'nhap'),
                                                      ('bsd_thanh_toan', '!=', 'da_tt')])
        for dat_coc in dat_coc_ids:
            self.bsd_ct_ids.create({
                'bsd_dat_coc_id': dat_coc.id,
                'bsd_so_ct': dat_coc.bsd_ma_dat_coc,
                'bsd_loai_ct': 'pt_dc',
                'bsd_tien': dat_coc.bsd_tien_dc,
                'bsd_tien_phai_tt': dat_coc.bsd_tien_phai_tt,
                'bsd_can_tru_id': self.id,
            })
        # Lấy chứng từ đợt thanh toán của đặt cọc
        dot_tt_ids = self.env['bsd.cong_no'].search([('bsd_khach_hang_id', '=', self.bsd_khach_hang_id.id),
                                                     ('bsd_dot_tt_id', '!=', False)]).mapped('bsd_dot_tt_id')
        for dot_tt in dot_tt_ids.filtered(lambda x: x.bsd_thanh_toan != 'da_tt'):
            if dot_tt.bsd_gd_tt == 'dat_coc':
                _logger.debug("dat coc")
                _logger.debug(dot_tt.bsd_dat_coc_id)
                self.bsd_ct_ids.create({
                    'bsd_dot_tt_id': dot_tt.id,
                    'bsd_dat_coc_id': dot_tt.bsd_dat_coc_id.id,
                    'bsd_so_ct': dot_tt.bsd_ten_dtt,
                    'bsd_loai_ct': 'pt_dtt',
                    'bsd_tien': dot_tt.bsd_tien_dot_tt,
                    'bsd_tien_phai_tt': dot_tt.bsd_tien_phai_tt,
                    'bsd_can_tru_id': self.id,
                })
            else:
                _logger.debug("dat coc")
                _logger.debug(dot_tt.bsd_hd_ban_id)
                self.bsd_ct_ids.create({
                    'bsd_dot_tt_id': dot_tt.id,
                    'bsd_hd_ban_id': dot_tt.bsd_hd_ban_id.id,
                    'bsd_so_ct': dot_tt.bsd_ten_dtt,
                    'bsd_loai_ct': 'pt_dtt',
                    'bsd_tien': dot_tt.bsd_tien_dot_tt,
                    'bsd_tien_phai_tt': dot_tt.bsd_tien_phai_tt,
                    'bsd_can_tru_id': self.id,
                })

    # TC.04.03 Cấn trừ công nợ
    def action_can_tru(self):
        self.write({
            'state': 'can_tru'
        })
        # Xóa chứng từ không cấn trừ
        self.bsd_ct_ids.filtered(lambda x: x.bsd_tien_can_tru <= 0).unlink()
        for ct in self.bsd_ct_ids:
            self.env['bsd.cong_no_ct'].create({
                'bsd_ngay_pb': self.bsd_ngay_can_tru,
                'bsd_khach_hang_id': self.bsd_khach_hang_id.id,
                'bsd_gc_tc_id': ct.bsd_gc_tc_id.id,
                'bsd_giu_cho_id': ct.bsd_giu_cho_id.id,
                'bsd_dat_coc_id': ct.bsd_dat_coc_id.id,
                'bsd_hd_ban_id': ct.bsd_hd_ban_id.id,
                'bsd_dot_tt_id': ct.bsd_dot_tt_id.id,
                'bsd_phieu_thu_id': self.bsd_phieu_thu_id.id,
                'bsd_tien_pb': ct.bsd_tien_can_tru,
                'bsd_loai': ct.bsd_loai_ct,
                'state': 'hoan_thanh',
                'bsd_can_tru_id': self.id,
            })

    # TC.04.04 Hủy cấn trừ
    def action_huy_can_tru(self):
        self.write({
            'state': 'huy_ct',
        })
        self.env['bsd.cong_no_ct'].search([('bsd_can_tru_id', '=', self.id)]).unlink()


class BsdCanTruChiTiet(models.Model):
    _name = 'bsd.can_tru_ct'
    _description = 'Cấn trừ công nợ chi tiết'
    _rec_name = 'bsd_so_ct'

    bsd_can_tru_id = fields.Many2one('bsd.can_tru', string="Cấn trừ")
    bsd_loai_ct = fields.Selection([('pt_gctc', 'Giữ chỗ thiện chí'),
                                    ('pt_gc', 'Giữ chỗ'),
                                    ('pt_dc', 'Đặt cọc'),
                                    ('pt_dtt', 'Đợt thanh toán')], string="Loại chứng từ",
                                   help="Loại chứng từ", readonly=True)
    bsd_so_ct = fields.Char(string="Số chứng từ", help="Số chứng từ", readonly=True)
    bsd_ngay_ct = fields.Datetime(string="Ngày chứng từ", help="Ngày chứng từ", readonly=True)
    bsd_tien = fields.Monetary(string="Tiền", help="Tiền trên chứng từ", readonly=True)
    bsd_tien_phai_tt = fields.Monetary(string="Phải thanh toán", help="Phải thanh toán", readonly=True)
    bsd_tien_can_tru = fields.Monetary(string="Tiền cấn trừ", help="Tiền cấn trừ")

    bsd_gc_tc_id = fields.Many2one('bsd.gc_tc', string="Giữ chỗ thiện chí", help="Giữ chỗ thiện chí", readonly=True)
    bsd_giu_cho_id = fields.Many2one('bsd.giu_cho', string="Giữ chỗ", help="Giữ chỗ", readonly=True)
    bsd_dat_coc_id = fields.Many2one('bsd.dat_coc', string="Đặt cọc", help="Đặt cọc", readonly=True)
    bsd_hd_ban_id = fields.Many2one('bsd.hd_ban', string="Hợp đồng", help="Hợp đồng", readonly=True)
    bsd_dot_tt_id = fields.Many2one('bsd.lich_thanh_toan', string="Đợt thanh toán", readonly=True)
    company_id = fields.Many2one('res.company', string='Công ty', default=lambda self: self.env.company)
    currency_id = fields.Many2one(related="company_id.currency_id", string="Tiền tệ", readonly=True)

    @api.constrains('bsd_tien_can_tru')
    def _constrains_tien_can_tru(self):
        if self.bsd_tien_can_tru > self.bsd_tien_phai_tt:
            raise UserError("Tiền cấn trừ không thể lớn hơn tiền phải thanh toán")

