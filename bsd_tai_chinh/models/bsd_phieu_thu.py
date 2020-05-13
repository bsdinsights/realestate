# -*- coding:utf-8 -*-

from odoo import models, fields, api
from odoo.exceptions import UserError
import logging
_logger = logging.getLogger(__name__)


class BsdPhieuThu(models.Model):
    _name = 'bsd.phieu_thu'
    _description = 'Phiếu thu'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _rec_name = 'bsd_so_pt'

    bsd_so_pt = fields.Char(string="Số phiếu thu", help="Số phiếu thu", required=True,
                            readonly=True,
                            states={'nhap': [('readonly', False)]})
    _sql_constraints = [
        ('bsd_so_pt_unique', 'unique (bsd_so_pt)',
         'Số phiếu thu đã tồn tại !'),
    ]
    bsd_ngay_pt = fields.Datetime(string="Ngày", help="Ngày phiếu thu", required=True,
                                  readonly=True, default=lambda self: fields.Datetime.now(),
                                  states={'nhap': [('readonly', False)]})
    bsd_loai_pt = fields.Selection([('tra_truoc', 'Trả trước'),
                                    ('gc_tc', 'Giữ chỗ thiện chí'),
                                    ('giu_cho', 'Giữ chỗ'),
                                    ('dat_coc', 'Đặt cọc'),
                                    ('dot_tt', 'Đợt thanh toán'),
                                    ('khac', 'Khác')], default="tra_truoc", required=True, string="Loại phiếu thu",
                                   readonly=True,
                                   states={'nhap': [('readonly', False)]})
    bsd_loai_hd = fields.Selection([('dat_coc', 'Đặt cọc'),
                                    ('hd_ban', 'Hợp đồng bán')], string="Loại hợp đồng",
                                   help="""Thông tin ghi nhận thu tiền theo đợt thanh toán 
                                           của Đặt cọc hay hợp đồng bán""",
                                   readonly=True,
                                   states={'nhap': [('readonly', False)]})
    bsd_khach_hang_id = fields.Many2one('res.partner', string="Khách hàng", help="Tên khách hàng", required=True,
                                        readonly=True,
                                        states={'nhap': [('readonly', False)]})
    bsd_pt_tt_id = fields.Many2one('bsd.pt_tt', string="Phương thức", help="Phương thức thanh toán", required=True,
                                   readonly=True,
                                   states={'nhap': [('readonly', False)]})
    bsd_so_nk = fields.Selection([('tien_mat', 'Tiền mặt'), ('ngan_hang', 'Ngân hàng')], string="Sổ nhật ký",
                                 required=True,
                                 readonly=True,
                                 states={'nhap': [('readonly', False)]}, default="tien_mat")
    bsd_tk_nh_id = fields.Many2one('res.partner.bank', string="Tài khoản ngân hàng",
                                   help="Số tài khoản ngân hàng của chủ sở hữu",
                                   readonly=True,
                                   states={'nhap': [('readonly', False)]})
    bsd_ngan_hang_id = fields.Many2one('res.bank', string="Tên ngân hàng", help="Tên ngân hàng",
                                       readonly=True,
                                       states={'nhap': [('readonly', False)]})
    bsd_du_an_id = fields.Many2one('bsd.du_an', string="Dự án", help="Tên dự án", required=True,
                                   readonly=True,
                                   states={'nhap': [('readonly', False)]})
    bsd_unit_id = fields.Many2one('product.product', string="Căn hộ",
                                  readonly=True,
                                  states={'nhap': [('readonly', False)]})
    bsd_gc_tc_id = fields.Many2one('bsd.gc_tc', string="Giữ chỗ thiện chí", help="Giữ chỗ thiện chí",
                                   readonly=True,
                                   states={'nhap': [('readonly', False)]})
    bsd_giu_cho_id = fields.Many2one('bsd.giu_cho', string="Giữ chỗ", help="Giữ chỗ",
                                     readonly=True,
                                     states={'nhap': [('readonly', False)]})
    bsd_dat_coc_id = fields.Many2one('bsd.dat_coc', string="Đặt cọc", help="Đặt cọc",
                                     readonly=True,
                                     states={'nhap': [('readonly', False)]})
    bsd_hd_ban_id = fields.Many2one('bsd.hd_ban', string="Hợp đồng", help="Hợp đồng",
                                    readonly=True,
                                    states={'nhap': [('readonly', False)]})
    bsd_dot_tt_id = fields.Many2one('bsd.lich_thanh_toan', string="Đợt thanh toán",
                                    readonly=True,
                                    states={'nhap': [('readonly', False)]})
    bsd_tien = fields.Monetary(string="Tiền", help="Tiền", required=True,
                               readonly=True,
                               states={'nhap': [('readonly', False)]})
    bsd_tien_da_tt = fields.Monetary(string="Tiền đã thanh toán", help="Tiền đã thanh toán",
                                     compute='_compute_tien_ct', store=True)
    bsd_tien_con_lai = fields.Monetary(string="Tiền còn lại", help="Tiền còn lại",
                                       compute='_compute_tien_ct', store=True)
    bsd_ct_ids = fields.One2many('bsd.cong_no_ct', 'bsd_phieu_thu_id', string="Công nợ chứng tự", readonly=True)
    bsd_dien_giai = fields.Char(string="Diễn giải", help="Diễn giải",
                                readonly=True,
                                states={'nhap': [('readonly', False)]})

    company_id = fields.Many2one('res.company', string='Công ty', default=lambda self: self.env.company)
    currency_id = fields.Many2one(related="company_id.currency_id", string="Tiền tệ", readonly=True)

    state = fields.Selection([('nhap', 'Nháp'), ('da_xn', 'Đã xác nhận'),
                              ('da_gs', 'Đã ghi sổ'), ('huy', 'Hủy')], string="Trạng thái", help="Trạng thái",
                             required=True, readonly=True, default='nhap', tracking=1)

    @api.depends('bsd_ct_ids', 'bsd_ct_ids.bsd_tien_pb', 'bsd_tien')
    def _compute_tien_ct(self):
        _logger.debug("Tính toán lại tiền phiếu thu")
        for each in self:
            each.bsd_tien_da_tt = sum(each.bsd_ct_ids.mapped('bsd_tien_pb'))
            each.bsd_tien_con_lai = each.bsd_tien - each.bsd_tien_da_tt

    @api.onchange('bsd_loai_pt', 'bsd_gc_tc_id', 'bsd_dot_tt_id', 'bsd_dat_coc_id', 'bsd_giu_cho_id')
    def _onchange_tien(self):
        _logger.debug("onchange tiền")
        if self.bsd_loai_pt == 'gc_tc' and self.bsd_gc_tc_id:
            gc_tc = self.env['bsd.gc_tc'].search([('id', '=', self.bsd_gc_tc_id.id)])
            self.bsd_tien = gc_tc.bsd_tien_phai_tt

        if self.bsd_loai_pt == 'giu_cho' and self.bsd_giu_cho_id:
            giu_cho = self.env['bsd.giu_cho'].search([('id', '=', self.bsd_giu_cho_id.id)])
            self.bsd_tien = giu_cho.bsd_tien_phai_tt

        if self.bsd_loai_pt == 'dat_coc' and self.bsd_dat_coc_id:
            dat_coc = self.env['bsd.dat_coc'].search([('id', '=', self.bsd_dat_coc_id.id)])
            self.bsd_tien = dat_coc.bsd_tien_phai_tt

        if self.bsd_loai_pt == 'dot_tt' and self.bsd_dot_tt_id:
            dot_tt = self.env['bsd.lich_thanh_toan'].search([('id', '=', self.bsd_dot_tt_id.id)])
            self.bsd_tien = dot_tt.bsd_tien_phai_tt

    @api.onchange('bsd_loai_pt')
    def _onchange_loai_sp(self):
        if self.bsd_loai_pt == 'dot_tt':
            self.bsd_loai_hd = 'dat_coc'
        else:
            self.bsd_loai_hd = None

    @api.onchange('bsd_dat_coc_id', 'bsd_hd_ban_id', 'bsd_loai_hd')
    def _onchange_dot_tt(self):
        res = {}
        if self.bsd_loai_hd == 'dat_coc':
            res.update({
                'domain': {'bsd_dot_tt_id': [('bsd_dat_coc_id', '=', self.bsd_dat_coc_id.id),
                                             ('bsd_dat_coc_id', '!=', False),
                                             ('bsd_gd_tt', '=', 'dat_coc')]}
            })
        else:
            res.update({
                'domain': {'bsd_dot_tt_id': [('bsd_hd_ban_id', '=', self.bsd_hd_ban_id.id),
                                             ('bsd_hd_ban_id', '!=', False),
                                             ('bsd_gd_tt', '=', 'hop_dong')]}
            })
        return res

    # TC.01.01 Xác nhận phiếu thu
    def action_xac_nhan(self):
        self.write({
            'state': 'da_xn',
        })

    # Nút vào sổ
    def action_vao_so(self):
        if self.bsd_loai_pt == 'tra_truoc':
            self._gs_pt_tra_trươc()
        elif self.bsd_loai_pt == 'khac':
            self._gs_pt_khac()
        elif self.bsd_loai_pt == 'gc_tc':
            self._gs_pt_gc_tc()
        elif self.bsd_loai_pt == 'giu_cho':
            self._gs_pt_giu_cho()
        elif self.bsd_loai_pt == 'dat_coc':
            self._gs_pt_dat_coc()
        elif self.bsd_loai_pt == 'dot_tt':
            if self.bsd_loai_hd == 'dat_coc':
                self._gs_pt_dot_tt_dc()
            else:
                self._gs_pt_dot_tt_hd()
        else:
            pass

        self.write({
            'state': 'da_gs',
        })

    # TC.01.02 Ghi sổ phiếu thu trả trước
    def _gs_pt_tra_trươc(self):
        self.env['bsd.cong_no'].create({
                'bsd_chung_tu': self.bsd_so_pt,
                'bsd_ngay': self.bsd_ngay_pt,
                'bsd_khach_hang_id': self.bsd_khach_hang_id.id,
                'bsd_du_an_id': self.bsd_du_an_id.id,
                'bsd_ps_giam': self.bsd_tien,
                'bsd_ps_tang': 0,
                'bsd_loai_ct': 'phieu_thu',
                'bsd_phat_sinh': 'giam',
                'bsd_phieu_thu_id': self.id,
                'state': 'da_gs',
            })

    # TC.01.03 - Ghi số phiếu thu Giữ chỗ thiện chí
    def _gs_pt_gc_tc(self):
        # ghi công nợ giảm
        giam_id = self.env['bsd.cong_no'].create({
                        'bsd_chung_tu': self.bsd_so_pt,
                        'bsd_ngay': self.bsd_ngay_pt,
                        'bsd_khach_hang_id': self.bsd_khach_hang_id.id,
                        'bsd_du_an_id': self.bsd_du_an_id.id,
                        'bsd_ps_giam': self.bsd_tien,
                        'bsd_ps_tang': 0,
                        'bsd_loai_ct': 'phieu_thu',
                        'bsd_phat_sinh': 'giam',
                        'bsd_phieu_thu_id': self.id,
                        'state': 'da_gs',
        })
        # tạo record trong bảng công nợ chứng từ
        self.env['bsd.cong_no_ct'].create({
            'bsd_ngay_pb': self.bsd_ngay_pt,
            'bsd_khach_hang_id': self.bsd_khach_hang_id.id,
            'bsd_gc_tc_id': self.bsd_gc_tc_id.id,
            'bsd_phieu_thu_id': self.id,
            'bsd_tien_pb': self.bsd_tien,
            'bsd_loai': 'pt_gctc',
            'state': 'hoan_thanh',
        })

    # TC.01.04 - Ghi số phiếu thu Giữ chỗ
    def _gs_pt_giu_cho(self):
        # ghi công nợ giảm
        giam_id = self.env['bsd.cong_no'].create({
                        'bsd_chung_tu': self.bsd_so_pt,
                        'bsd_ngay': self.bsd_ngay_pt,
                        'bsd_khach_hang_id': self.bsd_khach_hang_id.id,
                        'bsd_du_an_id': self.bsd_du_an_id.id,
                        'bsd_ps_giam': self.bsd_tien,
                        'bsd_ps_tang': 0,
                        'bsd_loai_ct': 'phieu_thu',
                        'bsd_phat_sinh': 'giam',
                        'bsd_phieu_thu_id': self.id,
                        'state': 'da_gs',
        })
        # tạo record trong bảng công nợ chứng từ
        self.env['bsd.cong_no_ct'].create({
            'bsd_ngay_pb': self.bsd_ngay_pt,
            'bsd_khach_hang_id': self.bsd_khach_hang_id.id,
            'bsd_giu_cho_id': self.bsd_giu_cho_id.id,
            'bsd_phieu_thu_id': self.id,
            'bsd_tien_pb': self.bsd_tien,
            'bsd_loai': 'pt_gc',
            'state': 'hoan_thanh',
        })

    # TC.01.05 Ghi sổ phiếu thu Đặt cọc
    def _gs_pt_dat_coc(self):
        # ghi công nợ giảm
        giam_id = self.env['bsd.cong_no'].create({
                        'bsd_chung_tu': self.bsd_so_pt,
                        'bsd_ngay': self.bsd_ngay_pt,
                        'bsd_khach_hang_id': self.bsd_khach_hang_id.id,
                        'bsd_du_an_id': self.bsd_du_an_id.id,
                        'bsd_ps_giam': self.bsd_tien,
                        'bsd_ps_tang': 0,
                        'bsd_loai_ct': 'phieu_thu',
                        'bsd_phat_sinh': 'giam',
                        'bsd_phieu_thu_id': self.id,
                        'state': 'da_gs',
        })
        # tạo record trong bảng công nợ chứng từ
        self.env['bsd.cong_no_ct'].create({
            'bsd_ngay_pb': self.bsd_ngay_pt,
            'bsd_khach_hang_id': self.bsd_khach_hang_id.id,
            'bsd_dat_coc_id': self.bsd_dat_coc_id.id,
            'bsd_phieu_thu_id': self.id,
            'bsd_tien_pb': self.bsd_tien,
            'bsd_loai': 'pt_dc',
            'state': 'hoan_thanh',
        })

    # TC.01.06 Ghi sổ phiếu thu đợt thanh toán
    def _gs_pt_dot_tt_dc(self):
        # ghi công nợ giảm
        giam_id = self.env['bsd.cong_no'].create({
                        'bsd_chung_tu': self.bsd_so_pt,
                        'bsd_ngay': self.bsd_ngay_pt,
                        'bsd_khach_hang_id': self.bsd_khach_hang_id.id,
                        'bsd_du_an_id': self.bsd_du_an_id.id,
                        'bsd_ps_giam': self.bsd_tien,
                        'bsd_ps_tang': 0,
                        'bsd_loai_ct': 'phieu_thu',
                        'bsd_phat_sinh': 'giam',
                        'bsd_phieu_thu_id': self.id,
                        'state': 'da_gs',
        })
        # tạo record trong bảng công nợ chứng từ
        self.env['bsd.cong_no_ct'].create({
            'bsd_ngay_pb': self.bsd_ngay_pt,
            'bsd_khach_hang_id': self.bsd_khach_hang_id.id,
            'bsd_phieu_thu_id': self.id,
            'bsd_dat_coc_id': self.bsd_dat_coc_id.id,
            'bsd_dot_tt_id': self.bsd_dot_tt_id.id,
            'bsd_tien_pb': self.bsd_tien,
            'bsd_loai': 'pt_dtt',
            'state': 'hoan_thanh',
        })

    # TC.01.06 Ghi sổ phiếu đợt thanh toán hợp đồng bán
    def _gs_pt_dot_tt_hd(self):
        # ghi công nợ giảm
        giam_id = self.env['bsd.cong_no'].create({
                        'bsd_chung_tu': self.bsd_so_pt,
                        'bsd_ngay': self.bsd_ngay_pt,
                        'bsd_khach_hang_id': self.bsd_khach_hang_id.id,
                        'bsd_du_an_id': self.bsd_du_an_id.id,
                        'bsd_ps_giam': self.bsd_tien,
                        'bsd_ps_tang': 0,
                        'bsd_loai_ct': 'phieu_thu',
                        'bsd_phat_sinh': 'giam',
                        'bsd_phieu_thu_id': self.id,
                        'state': 'da_gs',
        })
        # tạo record trong bảng công nợ chứng từ
        self.env['bsd.cong_no_ct'].create({
            'bsd_ngay_pb': self.bsd_ngay_pt,
            'bsd_khach_hang_id': self.bsd_khach_hang_id.id,
            'bsd_phieu_thu_id': self.id,
            'bsd_hd_ban_id': self.bsd_hd_ban_id.id,
            'bsd_dot_tt_id': self.bsd_dot_tt_id.id,
            'bsd_tien_pb': self.bsd_tien,
            'bsd_loai': 'pt_dtt',
            'state': 'hoan_thanh',
        })

    # TC.01.07 Ghi sổ phiếu thu khác
    def _gs_pt_khac(self):
        self.env['bsd.cong_no'].create({
                'bsd_ngay': self.bsd_ngay_pt,
                'bsd_khach_hang_id': self.bsd_khach_hang_id.id,
                'bsd_du_an_id': self.bsd_du_an_id.id,
                'bsd_ps_giam': self.bsd_tien,
                'bsd_ps_tang': 0,
                'bsd_loai_ct': 'phieu_thu',
                'bsd_phat_sinh': 'giam',
                'bsd_phieu_thu_id': self.id,
                'state': 'da_gs',
            })

    # TC.01.08 - Kiểm tra thanh toán dư
    @api.constrains('bsd_tien')
    def _constrain_tien(self):
        _logger.debug("Kiểm tra field tiền")
        bsd_tien_phai_tt = 0
        flag = False
        if self.bsd_loai_pt == 'gc_tc' and self.bsd_gc_tc_id:
            cong_no_ct = self.env['bsd.cong_no_ct'].search([('bsd_gc_tc_id', '=', self.bsd_gc_tc_id.id)])
            if cong_no_ct:
                bsd_tien_phai_tt = self.bsd_gc_tc_id.bsd_tien_gc - sum(cong_no_ct.mapped('bsd_tien_pb'))
            else:
                bsd_tien_phai_tt = self.bsd_gc_tc_id.bsd_tien_gc
            if self.bsd_tien > bsd_tien_phai_tt:
                flag = True
        if self.bsd_loai_pt == 'giu_cho' and self.bsd_giu_cho_id:
            cong_no_ct = self.env['bsd.cong_no_ct'].search([('bsd_giu_cho_id', '=', self.bsd_giu_cho_id.id)])
            if cong_no_ct:
                bsd_tien_phai_tt = self.bsd_giu_cho_id.bsd_tien_gc - sum(cong_no_ct.mapped('bsd_tien_pb'))
            else:
                bsd_tien_phai_tt = self.bsd_giu_cho_id.bsd_tien_gc
            if self.bsd_tien > bsd_tien_phai_tt:
                flag = True
        if self.bsd_loai_pt == 'dat_coc' and self.bsd_dat_coc_id:
            cong_no_ct = self.env['bsd.cong_no_ct'].search([('bsd_dat_coc_id', '=', self.bsd_dat_coc_id.id),
                                                            ('bsd_dot_tt_id', '=', False)])
            if cong_no_ct:
                bsd_tien_phai_tt = self.bsd_dat_coc_id.bsd_tien_dc - sum(cong_no_ct.mapped('bsd_tien_pb'))
            else:
                bsd_tien_phai_tt = self.bsd_dat_coc_id.bsd_tien_dc
            if self.bsd_tien > bsd_tien_phai_tt:
                flag = True
        if self.bsd_loai_pt == 'dot_tt' and self.bsd_dot_tt_id:
            cong_no_ct = self.env['bsd.cong_no_ct'].search([('bsd_dot_tt_id', '=', self.bsd_dot_tt_id.id)])
            if cong_no_ct:
                bsd_tien_phai_tt = self.bsd_dot_tt_id.bsd_tien_dot_tt - sum(cong_no_ct.mapped('bsd_tien_pb'))
            else:
                bsd_tien_phai_tt = self.bsd_dot_tt_id.bsd_tien_dot_tt
            if self.bsd_tien > bsd_tien_phai_tt:
                flag = True
        if flag:
            raise UserError("Tiền phải thu vượt quá số tiền còn lại. Vui lòng kiểm tra lại!")
