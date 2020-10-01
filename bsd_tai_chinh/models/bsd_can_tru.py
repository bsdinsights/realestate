# -*- coding:utf-8 -*-

from odoo import models, fields, api, _
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
    bsd_ma_kh = fields.Char(string="Mã khách hàng", help="Mã khách hàng", required=True, readonly=True,
                            states={'nhap': [('readonly', False)]})
    bsd_khach_hang_id = fields.Many2one("res.partner", string="Tên khách hàng", help="Tên khách hàng", required=True,
                                        readonly=True,
                                        states={'nhap': [('readonly', False)]})
    bsd_ngay_can_tru = fields.Datetime(string="Ngày cấn trừ", help="Ngày cấn trừ", required=True,
                                       default=lambda self: fields.Datetime.now(), readonly=True,
                                       states={'nhap': [('readonly', False)]})
    bsd_tien_can_tru = fields.Monetary(string="Tiền cấn trừ", compute='_compute_tien_can_tru', store=True)
    bsd_loai_ct = fields.Selection([('phieu_thu', 'Phiếu thanh toán')], string="Loại chứng từ", help="Loại chứng từ",
                                   required=True, readonly=True, default='phieu_thu',
                                   states={'nhap': [('readonly', False)]})
    bsd_phieu_thu_id = fields.Many2one('bsd.phieu_thu', string="Phiếu thanh toán", help="Phiếu thanh toán", readonly=True,
                                       states={'nhap': [('readonly', False)]})
    bsd_hd_ban_id = fields.Many2one('bsd.hd_ban', string="Hợp đồng", help="Điều kiện lọc thêm hợp đồng")
    bsd_dot_tt_id = fields.Many2one('bsd.lich_thanh_toan', string="Đợt thanh toán", help="Lọc phí phát sinh theo đợt")

    bsd_loai = fields.Selection([('tat_ca', 'Tất cả'),
                                 ('dtt', 'Đợt thanh toán'),
                                 ('pps', 'Phí phát sinh')], string="Lọc theo",
                                help="Phân loại lọc dữ liệu",
                                default='tat_ca', required=True)
    bsd_ngay_ct = fields.Datetime(string="Ngày chứng từ", help="Ngày chứng từ", related='bsd_phieu_thu_id.bsd_ngay_pt')
    bsd_tien_con_lai = fields.Monetary(related="bsd_phieu_thu_id.bsd_tien_con_lai", store=True)
    state = fields.Selection([('nhap', 'Nháp'),
                              ('can_tru', 'Cấn trừ'),
                              ('huy_ct', 'Hủy cấn trừ')], string="Trạng thái", requried=True, tracking=1,
                             default='nhap', readonly=True)
    bsd_ct_ids = fields.One2many('bsd.can_tru_ct', 'bsd_can_tru_id', string="Chi tiết", readonly=True,
                                 states={'nhap': [('readonly', False)]})

    @api.onchange('bsd_khach_hang_id')
    def _onchange_ma_kh(self):
        self.bsd_ma_kh = self.bsd_khach_hang_id.bsd_ma_kh

    # TC.04.02 So sánh tiền cấn trừ và tiền còn lại
    @api.constrains('bsd_tien_can_tru')
    def _constrains_tien_can_tru(self):
        if self.bsd_tien_can_tru > self.bsd_tien_con_lai:
            raise UserError("Tiền cấn trừ không thể lớn hơn tiền còn lại.")

    @api.depends('bsd_ct_ids', 'bsd_ct_ids.bsd_tien_can_tru')
    def _compute_tien_can_tru(self):
        for each in self:
            each.bsd_tien_can_tru = sum(each.bsd_ct_ids.mapped('bsd_tien_can_tru'))

    # TC.04.01 Load chứng từ cần cấn trừ
    def action_load(self):
        # Xóa bảng chi tiết không được cấn trừ
        self.bsd_ct_ids.filtered(lambda x: x.bsd_tien_can_tru <= 0).unlink()
        if self.bsd_loai == 'tat_ca':
            # Lấy chứng từ giữ chỗ thiện chí
            # gc_tc_ids = self.env['bsd.cong_no'].search([('bsd_khach_hang_id', '=', self.bsd_khach_hang_id.id),
            #                                             ('bsd_loai_ct', '=', 'gc_tc'),
            #                                             ('bsd_gc_tc_id', '!=', False)]).mapped('bsd_gc_tc_id')
            # for gc_tc in gc_tc_ids.filtered(lambda x: x.bsd_thanh_toan != 'da_tt'):
            #     self.bsd_ct_ids.create({
            #         'bsd_gc_tc_id': gc_tc.id,
            #         'bsd_so_ct': gc_tc.bsd_ma_gctc,
            #         'bsd_loai_ct': 'pt_gctc',
            #         'bsd_tien': gc_tc.bsd_tien_gc,
            #         'bsd_tien_phai_tt': gc_tc.bsd_tien_phai_tt,
            #         'bsd_can_tru_id': self.id,
            #     })
            # Lấy chứng từ giữ chỗ
            # giu_cho_ids = self.env['bsd.cong_no'].search([('bsd_khach_hang_id', '=', self.bsd_khach_hang_id.id),
            #                                               ('bsd_loai_ct', '=', 'giu_cho'),
            #                                               ('bsd_giu_cho_id', '!=', False)]).mapped('bsd_giu_cho_id')
            # for giu_cho in giu_cho_ids.filtered(lambda x: x.bsd_thanh_toan != 'da_tt'):
            #     self.bsd_ct_ids.create({
            #         'bsd_giu_cho_id': giu_cho.id,
            #         'bsd_so_ct': giu_cho.bsd_ma_gc,
            #         'bsd_loai_ct': 'pt_gc',
            #         'bsd_tien': giu_cho.bsd_tien_gc,
            #         'bsd_tien_phai_tt': giu_cho.bsd_tien_phai_tt,
            #         'bsd_can_tru_id': self.id,
            #     })

            # Lấy chứng từ đặt cọc
            # dat_coc_ids = self.env['bsd.cong_no'].search([('bsd_khach_hang_id', '=', self.bsd_khach_hang_id.id),
            #                                               ('bsd_loai_ct', '=', 'dat_coc'),
            #                                               ('bsd_dat_coc_id', '!=', False),
            #                                               ('bsd_dot_tt_id', '=', False)]).mapped('bsd_dat_coc_id')
            # for dat_coc in dat_coc_ids.filtered(lambda x: x.bsd_thanh_toan != 'da_tt'):
            #     self.bsd_ct_ids.create({
            #         'bsd_dat_coc_id': dat_coc.id,
            #         'bsd_so_ct': dat_coc.bsd_ma_dat_coc,
            #         'bsd_loai_ct': 'pt_dc',
            #         'bsd_tien': dat_coc.bsd_tien_dc,
            #         'bsd_tien_phai_tt': dat_coc.bsd_tien_phai_tt,
            #         'bsd_can_tru_id': self.id,
            #     })
            # Lấy chứng từ đợt thanh toán
            dot_tt_ids = self.env['bsd.cong_no'].search([('bsd_khach_hang_id', '=', self.bsd_khach_hang_id.id),
                                                         ('bsd_dot_tt_id', '!=', False)]).mapped('bsd_dot_tt_id')
            for dot_tt in dot_tt_ids.filtered(lambda x: x.bsd_thanh_toan != 'da_tt'):
                self.bsd_ct_ids.create({
                        'bsd_dot_tt_id': dot_tt.id,
                        'bsd_hd_ban_id': dot_tt.bsd_hd_ban_id.id,
                        'bsd_so_ct': dot_tt.bsd_ten_dtt,
                        'bsd_loai_ct': 'pt_dtt',
                        'bsd_tien': dot_tt.bsd_tien_dot_tt,
                        'bsd_tien_phai_tt': dot_tt.bsd_tien_phai_tt,
                        'bsd_can_tru_id': self.id,
                })
            # Lấy chứng từ phí phát sinh
            phi_ps_ids = self.env['bsd.cong_no'].search([('bsd_khach_hang_id', '=', self.bsd_khach_hang_id.id),
                                                         ('bsd_loai_ct', '=', 'phi_ps')])\
                .mapped('bsd_phi_ps_id').filtered(lambda x: x.bsd_thanh_toan != 'da_tt')
            for phi_ps in phi_ps_ids:
                self.bsd_ct_ids.create({
                        'bsd_phi_ps_id': phi_ps.id,
                        'bsd_dot_tt_id': phi_ps.bsd_dot_tt_id.id,
                        'bsd_hd_ban_id': phi_ps.bsd_hd_ban_id.id,
                        'bsd_so_ct': phi_ps.bsd_ma_ps,
                        'bsd_loai_ct': 'pt_pps',
                        'bsd_tien': phi_ps.bsd_tong_tien,
                        'bsd_tien_phai_tt': phi_ps.bsd_tien_phai_tt,
                        'bsd_can_tru_id': self.id,
                })
        elif self.bsd_loai == 'dtt':
            if not self.bsd_hd_ban_id:
                raise UserError(_('Vui lòng chọn hợp đồng.'))
            # Lấy chứng từ đợt thanh toán
            dot_tt_ids = self.env['bsd.cong_no'].search([('bsd_khach_hang_id', '=', self.bsd_khach_hang_id.id),
                                                         ('bsd_dot_tt_id', '!=', False),
                                                         ('bsd_hd_ban_id', '=', self.bsd_hd_ban_id.id)])\
                .mapped('bsd_dot_tt_id').filtered(lambda x: x.bsd_thanh_toan != 'da_tt')
            for dot_tt in dot_tt_ids:
                self.bsd_ct_ids.create({
                        'bsd_dot_tt_id': dot_tt.id,
                        'bsd_hd_ban_id': dot_tt.bsd_hd_ban_id.id,
                        'bsd_so_ct': dot_tt.bsd_ten_dtt,
                        'bsd_loai_ct': 'pt_dtt',
                        'bsd_tien': dot_tt.bsd_tien_dot_tt,
                        'bsd_tien_phai_tt': dot_tt.bsd_tien_phai_tt,
                        'bsd_can_tru_id': self.id,
                })
        elif self.bsd_loai == 'pps':
            phi_ps_ids = self.env['bsd.cong_no'].search([('bsd_khach_hang_id', '=', self.bsd_khach_hang_id.id),
                                                         ('bsd_loai_ct', '=', 'phi_ps')])\
                                                .mapped('bsd_phi_ps_id')\
                                                .filtered(lambda x: x.bsd_thanh_toan != 'da_tt')

            if not self.bsd_dot_tt_id and not self.bsd_hd_ban_id:
                # Lấy chứng từ phí phát sinh
                for phi_ps in phi_ps_ids:
                    self.bsd_ct_ids.create({
                            'bsd_phi_ps_id': phi_ps.id,
                            'bsd_dot_tt_id': phi_ps.bsd_dot_tt_id.id,
                            'bsd_hd_ban_id': phi_ps.bsd_hd_ban_id.id,
                            'bsd_so_ct': phi_ps.bsd_ma_ps,
                            'bsd_loai_ct': 'pt_pps',
                            'bsd_tien': phi_ps.bsd_tong_tien,
                            'bsd_tien_phai_tt': phi_ps.bsd_tien_phai_tt,
                            'bsd_can_tru_id': self.id,
                    })
            elif self.bsd_dot_tt_id and self.bsd_hd_ban_id:
                phi_ps_ids = phi_ps_ids.filtered(lambda x: x.bsd_dot_tt_id == self.bsd_dot_tt_id)
                # Lấy chứng từ phí phát sinh
                for phi_ps in phi_ps_ids:
                    self.bsd_ct_ids.create({
                            'bsd_phi_ps_id': phi_ps.id,
                            'bsd_dot_tt_id': phi_ps.bsd_dot_tt_id.id,
                            'bsd_hd_ban_id': phi_ps.bsd_hd_ban_id.id,
                            'bsd_so_ct': phi_ps.bsd_ma_ps,
                            'bsd_loai_ct': 'pt_pps',
                            'bsd_tien': phi_ps.bsd_tong_tien,
                            'bsd_tien_phai_tt': phi_ps.bsd_tien_phai_tt,
                            'bsd_can_tru_id': self.id,
                    })
            elif not self.bsd_dot_tt_id and self.bsd_hd_ban_id:
                phi_ps_ids = phi_ps_ids.filtered(lambda x: x.bsd_hd_ban_id == self.bsd_hd_ban_id)
                # Lấy chứng từ phí phát sinh
                for phi_ps in phi_ps_ids:
                    self.bsd_ct_ids.create({
                            'bsd_phi_ps_id': phi_ps.id,
                            'bsd_dot_tt_id': phi_ps.bsd_dot_tt_id.id,
                            'bsd_hd_ban_id': phi_ps.bsd_hd_ban_id.id,
                            'bsd_so_ct': phi_ps.bsd_ma_ps,
                            'bsd_loai_ct': 'pt_pps',
                            'bsd_tien': phi_ps.bsd_tong_tien,
                            'bsd_tien_phai_tt': phi_ps.bsd_tien_phai_tt,
                            'bsd_can_tru_id': self.id,
                    })

    # TC.04.03 Cấn trừ công nợ
    def action_can_tru(self):
        self.write({
            'state': 'can_tru'
        })
        # Xóa chứng từ không cấn trừ
        self.bsd_ct_ids.filtered(lambda x: x.bsd_tien_can_tru <= 0).unlink()
        # Lọc các công nợ là đợt thanh toán sorted theo số thứ tự
        ct_dtt = self.bsd_ct_ids.filtered(lambda x: x.bsd_dot_tt_id and not x.bsd_phi_ps_id)\
            .sorted(lambda x: x.bsd_dot_tt_id.bsd_stt)
        for ct in (self.bsd_ct_ids - ct_dtt):
            self.env['bsd.cong_no_ct'].create({
                'bsd_ngay_pb': self.bsd_ngay_can_tru,
                'bsd_khach_hang_id': self.bsd_khach_hang_id.id,
                'bsd_gc_tc_id': ct.bsd_gc_tc_id.id,
                'bsd_giu_cho_id': ct.bsd_giu_cho_id.id,
                'bsd_dat_coc_id': ct.bsd_dat_coc_id.id,
                'bsd_hd_ban_id': ct.bsd_hd_ban_id.id,
                'bsd_phi_ps_id': ct.bsd_phi_ps_id.id,
                'bsd_phieu_thu_id': self.bsd_phieu_thu_id.id,
                'bsd_tien_pb': ct.bsd_tien_can_tru,
                'bsd_loai': ct.bsd_loai_ct,
                'state': 'hoan_thanh',
                'bsd_can_tru_id': self.id,
            })
        for ct in ct_dtt:
            self.env['bsd.cong_no_ct'].create({
                'bsd_ngay_pb': self.bsd_ngay_can_tru,
                'bsd_khach_hang_id': self.bsd_khach_hang_id.id,
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
                                    ('pt_pps', 'Phí phát sinh'),
                                    ('pt_dtt', 'Đợt thanh toán')], string="Loại chứng từ",
                                   help="Loại chứng từ")
    bsd_so_ct = fields.Char(string="Số chứng từ", help="Số chứng từ")
    bsd_ngay_ct = fields.Datetime(string="Ngày chứng từ", help="Ngày chứng từ")
    bsd_tien = fields.Monetary(string="Tiền", help="Tiền trên chứng từ")
    bsd_tien_phai_tt = fields.Monetary(string="Phải thanh toán", help="Phải thanh toán",)
    bsd_tien_can_tru = fields.Monetary(string="Tiền cấn trừ", help="Tiền cấn trừ")

    bsd_gc_tc_id = fields.Many2one('bsd.gc_tc', string="Giữ chỗ thiện chí", help="Giữ chỗ thiện chí")
    bsd_giu_cho_id = fields.Many2one('bsd.giu_cho', string="Giữ chỗ", help="Giữ chỗ")
    bsd_dat_coc_id = fields.Many2one('bsd.dat_coc', string="Đặt cọc", help="Đặt cọc")
    bsd_hd_ban_id = fields.Many2one('bsd.hd_ban', string="Hợp đồng", help="Hợp đồng")
    bsd_dot_tt_id = fields.Many2one('bsd.lich_thanh_toan', string="Đợt thanh toán")
    bsd_phi_ps_id = fields.Many2one('bsd.phi_ps', string="Phí phát sinh")
    company_id = fields.Many2one('res.company', string='Công ty', default=lambda self: self.env.company)
    currency_id = fields.Many2one(related="company_id.currency_id", string="Tiền tệ", readonly=True)

    @api.constrains('bsd_tien_can_tru', 'bsd_tien_phai_tt')
    def _constrains_tien_can_tru(self):
        if self.bsd_tien_can_tru > self.bsd_tien_phai_tt:
            raise UserError("Tiền cấn trừ không thể lớn hơn tiền phải thanh toán.")

