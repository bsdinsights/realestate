# -*- coding:utf-8 -*-

from odoo import models, fields, api


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
                                  readonly=True, default=fields.Datetime.now(),
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
                                 states={'nhap': [('readonly', False)]})
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
    bsd_unit_id = fields.Many2one('product.product', string="Căn hộ")
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
    bsd_dien_giai = fields.Char(string="Diễn giải", help="Diễn giải",
                                readonly=True,
                                states={'nhap': [('readonly', False)]})

    company_id = fields.Many2one('res.company', string='Công ty', default=lambda self: self.env.company)
    currency_id = fields.Many2one(related="company_id.currency_id", string="Tiền tệ", readonly=True)

    state = fields.Selection([('nhap', 'Nháp'), ('da_xn', 'Đã xác nhận'),
                              ('da_gs', 'Đã ghi sổ'), ('huy', 'Hủy')], string="Trạng thái", help="Trạng thái",
                             required=True, readonly=True, default='nhap')

    @api.onchange('bsd_loai_pt')
    def _onchange_loai_sp(self):
        if self.bsd_loai_pt == 'dot_tt':
            self.bsd_loai_hd = 'dat_coc'
        else:
            self.bsd_loai_hd = None

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
                'bsd_tien': self.bsd_tien,
                'bsd_tien_thanh_toan': 0,
                'bsd_loai_ct': 'phieu_thu',
                'bsd_phat_sinh': 'giam',
                'bsd_phieu_thu_id': self.id,
                'bsd_phan_bo': 'chua_pb',
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
                        'bsd_tien': self.bsd_tien,
                        'bsd_tien_thanh_toan': self.bsd_tien,
                        'bsd_loai_ct': 'phieu_thu',
                        'bsd_phat_sinh': 'giam',
                        'bsd_phieu_thu_id': self.id,
                        'bsd_gc_tc_id': self.bsd_gc_tc_id.id,
                        'bsd_phan_bo': 'da_pb',
                        'state': 'da_gs',
        })
        # ghi công nợ tăng
        tang_id = self.env['bsd.cong_no'].search([('bsd_gc_tc_id', '=', self.bsd_gc_tc_id.id)], limit=1)

        # tạo record trong bảng công nợ chứng từ
        self.env['bsd.cong_no_ct'].create({
            'bsd_ngay_pb': self.bsd_ngay_pt,
            'bsd_khach_hang_id': self.bsd_khach_hang_id.id,
            'bsd_ps_tang_id': tang_id.id,
            'bsd_ps_giam_id': giam_id.id,
            'bsd_tien_pb': self.bsd_tien,
            'state': 'hoan_thanh',
        })
        # Ghi nhận số tiền đã thanh toán công nợ
        tang_id.write({
            'bsd_tien_thanh_toan': self.bsd_tien,
        })
        # Cập nhật lại giữ chỗ thiện chí
        if tang_id.bsd_tien_con_lai == 0:
            tang_id.bsd_gc_tc_id.write({
                'bsd_ngay_tt': self.bsd_ngay_pt,
                'bsd_thanh_toan': 'da_tt'
            })
            tang_id.write({
                'bsd_phan_bo': 'da_pb'
            })
        else:
            tang_id.bsd_gc_tc_id.write({
                'bsd_ngay_tt': self.bsd_ngay_pt,
                'bsd_thanh_toan': 'dang_tt'
            })

    # TC.01.04 - Ghi số phiếu thu Giữ chỗ
    def _gs_pt_giu_cho(self):
        # ghi công nợ giảm
        giam_id = self.env['bsd.cong_no'].create({
                        'bsd_chung_tu': self.bsd_so_pt,
                        'bsd_ngay': self.bsd_ngay_pt,
                        'bsd_khach_hang_id': self.bsd_khach_hang_id.id,
                        'bsd_du_an_id': self.bsd_du_an_id.id,
                        'bsd_tien': self.bsd_tien,
                        'bsd_tien_thanh_toan': self.bsd_tien,
                        'bsd_loai_ct': 'phieu_thu',
                        'bsd_phat_sinh': 'giam',
                        'bsd_phieu_thu_id': self.id,
                        'bsd_giu_cho_id': self.bsd_giu_cho_id.id,
                        'bsd_phan_bo': 'da_pb',
                        'state': 'da_gs',
        })
        # ghi công nợ tăng
        tang_id = self.env['bsd.cong_no'].search([('bsd_giu_cho_id', '=', self.bsd_giu_cho_id.id)], limit=1)

        # tạo record trong bảng công nợ chứng từ
        self.env['bsd.cong_no_ct'].create({
            'bsd_ngay_pb': self.bsd_ngay_pt,
            'bsd_khach_hang_id': self.bsd_khach_hang_id.id,
            'bsd_ps_tang_id': tang_id.id,
            'bsd_ps_giam_id': giam_id.id,
            'bsd_tien_pb': self.bsd_tien,
            'state': 'hoan_thanh',
        })
        # Ghi nhận số tiền đã thanh toán công nợ
        tang_id.write({
            'bsd_tien_thanh_toan': self.bsd_tien,
        })
        # Cập nhật lại giữ chỗ thiện chí
        if tang_id.bsd_tien_con_lai == 0:
            tang_id.bsd_giu_cho_id.write({
                'bsd_ngay_tt': self.bsd_ngay_pt,
                'bsd_thanh_toan': 'da_tt'
            })
            tang_id.write({
                'bsd_phan_bo': 'da_pb'
            })
        else:
            tang_id.bsd_giu_cho_id.write({
                'bsd_ngay_tt': self.bsd_ngay_pt,
                'bsd_thanh_toan': 'dang_tt'
            })

    # TC.01.07 Ghi sổ phiếu thu khác
    def _gs_pt_khac(self):
        self.env['bsd.cong_no'].create({
                'bsd_ngay': self.bsd_ngay_pt,
                'bsd_khach_hang_id': self.bsd_khach_hang_id.id,
                'bsd_du_an_id': self.bsd_du_an_id.id,
                'bsd_tien': self.bsd_tien,
                'bsd_tien_thanh_toan': 0,
                'bsd_loai_ct': 'phieu_thu',
                'bsd_phat_sinh': 'giam',
                'bsd_phieu_thu_id': self.id,
                'bsd_phan_bo': 'chua_pb',
                'state': 'da_gs',
            })