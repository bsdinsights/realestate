# -*- coding:utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError
import datetime
import logging
_logger = logging.getLogger(__name__)


class BsdPhieuThu(models.Model):
    _name = 'bsd.phieu_thu'
    _description = 'Phiếu thu'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _rec_name = 'bsd_so_pt'

    bsd_so_pt = fields.Char(string="Số", help="Số", required=True, readonly=True, copy=False,
                            default='/')
    _sql_constraints = [
        ('bsd_so_pt_unique', 'unique (bsd_so_pt)',
         'Số phiếu thu đã tồn tại !'),
    ]
    bsd_ngay_pt = fields.Datetime(string="Ngày thanh toán", help="Ngày thanh toán", required=True,
                                  readonly=True, default=lambda self: fields.Datetime.now(),
                                  states={'nhap': [('readonly', False)]})

    @api.constrains('bsd_ngay_pt')
    def _onchange_ngay_pt(self):
        today = datetime.date.today()
        if self.bsd_ngay_pt.date() > today:
            raise UserError(_("Ngày thanh toán không được lớn hơn ngày hiện tại."))

    def _get_pt(self):
        return self.env.ref('bsd_danh_muc.bsd_tien_mat').id

    bsd_loai_pt = fields.Selection([('tra_truoc', 'Trả trước'),
                                    ('gc_tc', 'Giữ chỗ thiện chí'),
                                    ('giu_cho', 'Giữ chỗ'),
                                    ('dat_coc', 'Đặt cọc'),
                                    ('dot_tt', 'Đợt thanh toán'),
                                    ('pql', 'Phí quản lý'),
                                    ('pbt', 'Phí bảo trì'),
                                    ('pps', 'Phí phát sinh'),
                                    ('hd', 'Hợp đồng')], default="tra_truoc", required=True, string="Loại",
                                   readonly=True,
                                   states={'nhap': [('readonly', False)]})
    bsd_khach_hang_id = fields.Many2one('res.partner', string="Khách hàng", help="Tên khách hàng", required=True,
                                        readonly=True,
                                        states={'nhap': [('readonly', False)]})
    bsd_pt_tt_id = fields.Many2one('bsd.pt_tt', string="Hình thức", help="Hình thức thanh toán",
                                   readonly=True, required=True, default=_get_pt,
                                   states={'nhap': [('readonly', False)]})
    bsd_so_nk = fields.Selection([('tien_mat', 'Tiền mặt'), ('ngan_hang', 'Ngân hàng')], string="Sổ nhật ký",
                                 required=True,
                                 readonly=True,
                                 states={'nhap': [('readonly', False)]}, default="tien_mat")
    bsd_tk_nh_id = fields.Many2one('res.partner.bank', string="Tài khoản ngân hàng",
                                   help="Số tài khoản ngân hàng của khách hàng",
                                   readonly=True,
                                   states={'nhap': [('readonly', False)]})
    bsd_ngan_hang_id = fields.Many2one('res.bank', string="Tên ngân hàng", help="Tên ngân hàng",
                                       readonly=True,
                                       states={'nhap': [('readonly', False)]})
    bsd_du_an_id = fields.Many2one('bsd.du_an', string="Dự án", help="Tên dự án", required=True,
                                   readonly=True,
                                   states={'nhap': [('readonly', False)]})
    bsd_unit_id = fields.Many2one('product.product', string="Sản phẩm",
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
    bsd_tien_kh = fields.Monetary(string="Tiền khách hàng", help="Số tiền thanh toán của khách hàng", required=True,
                                  readonly=True,
                                  states={'nhap': [('readonly', False)]})
    bsd_tien = fields.Monetary(string="Tiền thanh toán", help="Tiền thanh toán", readonly=1)
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

    state = fields.Selection([('nhap', 'Nháp'),
                              ('da_gs', 'Xác nhận'),
                              ('huy', 'Hủy')], string="Trạng thái", help="Trạng thái",
                             required=True, readonly=True, default='nhap', tracking=1)
    bsd_tien_lp_ut = fields.Monetary(string="Lãi phạt ước tính", help="Tiền lãi phạt ước tính thanh toán")
    bsd_tt_id = fields.Many2one(string="TT trả trước", help="Thanh toán trả trước khi thanh toán có dư", readonly=True)

    @api.depends('bsd_ct_ids', 'bsd_ct_ids.bsd_tien_pb', 'bsd_tien')
    def _compute_tien_ct(self):
        for each in self:
            each.bsd_tien_da_tt = sum(each.bsd_ct_ids
                                      .filtered(lambda x: x.state == 'hieu_luc')
                                      .mapped('bsd_tien_pb'))
            each.bsd_tien_con_lai = each.bsd_tien - each.bsd_tien_da_tt

    @api.onchange('bsd_loai_pt', 'bsd_gc_tc_id', 'bsd_dot_tt_id', 'bsd_dat_coc_id', 'bsd_giu_cho_id')
    def _onchange_tien(self):
        if self.bsd_loai_pt == 'gc_tc' and self.bsd_gc_tc_id:
            gc_tc = self.env['bsd.gc_tc'].search([('id', '=', self.bsd_gc_tc_id.id)])
            self.bsd_tien_kh = gc_tc.bsd_tien_phai_tt

        if self.bsd_loai_pt == 'giu_cho' and self.bsd_giu_cho_id:
            giu_cho = self.env['bsd.giu_cho'].search([('id', '=', self.bsd_giu_cho_id.id)])
            self.bsd_tien_kh = giu_cho.bsd_tien_phai_tt

        if self.bsd_loai_pt == 'dat_coc' and self.bsd_dat_coc_id:
            dat_coc = self.env['bsd.dat_coc'].search([('id', '=', self.bsd_dat_coc_id.id)])
            self.bsd_tien_kh = dat_coc.bsd_tien_phai_tt

        if self.bsd_loai_pt == 'hd' and self.bsd_dot_tt_id:
            dot_tt = self.env['bsd.lich_thanh_toan'].search([('id', '=', self.bsd_dot_tt_id.id)])
            self.bsd_tien_kh = dot_tt.bsd_tien_phai_tt

    @api.onchange('bsd_hd_ban_id', 'bsd_loai_pt')
    def _onchange_dot_tt(self):
        res = {}
        list_dtt = []
        if self.bsd_hd_ban_id and self.bsd_loai_pt == 'dot_tt':
            if self.bsd_hd_ban_id.state != 'nhap':
                list_dtt = self.bsd_hd_ban_id.bsd_ltt_ids.ids
        elif self.bsd_hd_ban_id and self.bsd_loai_pt == 'pql':
            pql = self.bsd_hd_ban_id.bsd_ltt_ids\
                                .filtered(lambda x: x.bsd_tinh_pql)\
                                .bsd_child_ids.filtered(lambda r: r.bsd_loai == 'pql')
            self.bsd_dot_tt_id = pql
            list_dtt = pql.ids
        elif self.bsd_hd_ban_id and self.bsd_loai_pt == 'pbt':
            pbt = self.bsd_hd_ban_id.bsd_ltt_ids\
                                .filtered(lambda x: x.bsd_tinh_pbt)\
                                .bsd_child_ids.filtered(lambda r: r.bsd_loai == 'pbt')
            self.bsd_dot_tt_id = pbt
            list_dtt = pbt.ids
        res.update({
                'domain': {'bsd_dot_tt_id': [('id', 'in', list_dtt), ('bsd_thanh_toan', '!=', 'da_tt')]}
            })

        return res

    # TC.01.01 Xác nhận phiếu thu
    def action_xac_nhan(self):
        # TC.01.09
        # Kiểm tra hợp đồng đã bị thanh lý chưa
        if self.bsd_hd_ban_id.state == 'thanh_ly':
            raise UserError(_('Hợp đồng đã bị thanh lý.\nVui lòng kiểm tra lại thông tin hợp đồng.'))
        # Kiểm tra nếu thu phí quản lý, phí bảo trì Sản phẩm phải có ngày cất nóc
        if self.bsd_loai_pt in ['pql', 'pbt']:
            if not self.bsd_unit_id.bsd_ngay_cn:
                raise UserError(_('Vui lòng kiểm tra thông tin sản phẩm trên hợp đồng.'))

        # Ghi nhận giờ ngày thanh toán
        now = datetime.datetime.now()
        get_time = self.bsd_ngay_pt.replace(hour=now.hour,
                                            minute=now.minute,
                                            second=now.second,
                                            microsecond=now.microsecond)

        # Kiểm tra thanh toán dư để tạo thanh toán trả trước
        co_tt_du, tien_tt_du, tien_tt = self._kiem_tra_tt_du()
        if co_tt_du:
            self.tao_tt_tra_truoc(tien_du=tien_tt_du)
        self.write({
            'bsd_tien': tien_tt,
            'state': 'da_gs',
            'bsd_ngay_pt': get_time
        })
        # thực hiện ghi nhận thanh toán
        if self.bsd_loai_pt == 'tra_truoc':
            self._gs_pt_tra_truoc(time=get_time)
        elif self.bsd_loai_pt == 'gc_tc':
            self._gs_pt_gc_tc(time=get_time)
        elif self.bsd_loai_pt == 'giu_cho':
            self._gs_pt_giu_cho(time=get_time)
        elif self.bsd_loai_pt == 'dat_coc':
            self._gs_pt_dat_coc(time=get_time)
        elif self.bsd_loai_pt in ['dot_tt', 'pql', 'pbt']:
            self._gs_pt_dot_tt_hd(time=get_time)
        elif self.bsd_loai_pt == 'pps':
            self._gs_pt_pps(time=get_time)
        else:
            pass
        # Cập nhật trạng thái hiệu lực các chi tiết
        for ct in self.bsd_ct_ids:
            ct.write({
                'bsd_ngay_pb': fields.Datetime.now(),
                'state': 'hieu_luc',
            })
            ct.kiem_tra_chung_tu()

    # TC.01.02 Ghi sổ phiếu thu trả trước
    def _gs_pt_tra_truoc(self, time):
        self.env['bsd.cong_no'].create({
                'bsd_chung_tu': self.bsd_so_pt,
                'bsd_ngay': time,
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
    def _gs_pt_gc_tc(self, time):
        # ghi công nợ giảm
        giam_id = self.env['bsd.cong_no'].create({
                        'bsd_chung_tu': self.bsd_so_pt,
                        'bsd_ngay': time,
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
        # self.env['bsd.cong_no_ct'].create({
        #     'bsd_ngay_pb': time,
        #     'bsd_khach_hang_id': self.bsd_khach_hang_id.id,
        #     'bsd_gc_tc_id': self.bsd_gc_tc_id.id,
        #     'bsd_phieu_thu_id': self.id,
        #     'bsd_tien_pb': self.bsd_tien,
        #     'bsd_loai': 'pt_gctc',
        #     'state': 'hieu_luc',
        # })

    # TC.01.04 - Ghi số phiếu thu Giữ chỗ
    def _gs_pt_giu_cho(self, time):
        # ghi công nợ giảm
        giam_id = self.env['bsd.cong_no'].create({
                        'bsd_chung_tu': self.bsd_so_pt,
                        'bsd_ngay': time,
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
        # self.env['bsd.cong_no_ct'].create({
        #     'bsd_ngay_pb': time,
        #     'bsd_khach_hang_id': self.bsd_khach_hang_id.id,
        #     'bsd_giu_cho_id': self.bsd_giu_cho_id.id,
        #     'bsd_phieu_thu_id': self.id,
        #     'bsd_tien_pb': self.bsd_tien,
        #     'bsd_loai': 'pt_gc',
        #     'state': 'hieu_luc',
        # })

    # TC.01.05 Ghi sổ phiếu thu Đặt cọc
    def _gs_pt_dat_coc(self, time):
        # ghi công nợ giảm
        giam_id = self.env['bsd.cong_no'].create({
                        'bsd_chung_tu': self.bsd_so_pt,
                        'bsd_ngay': time,
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
        # self.env['bsd.cong_no_ct'].create({
        #     'bsd_ngay_pb': time,
        #     'bsd_khach_hang_id': self.bsd_khach_hang_id.id,
        #     'bsd_dat_coc_id': self.bsd_dat_coc_id.id,
        #     'bsd_phieu_thu_id': self.id,
        #     'bsd_tien_pb': self.bsd_tien,
        #     'bsd_loai': 'pt_dc',
        #     'state': 'hieu_luc',
        # })

    # TC.01.06 Ghi sổ phiếu đợt thanh toán hợp đồng bán
    # TC.01.10 Ghi sổ phí quản lý, phí bảo trì là 1 đợt thanh toán
    def _gs_pt_dot_tt_hd(self, time):
        # Kiểm tra hợp đồng đã bị thanh lý chưa
        if self.bsd_hd_ban_id.state == 'thanh_ly':
            raise UserError(_('Hợp đồng đã bị thanh lý.\nVui lòng kiểm tra lại thông tin hợp đồng.'))
        # Kiểm tra nếu thu phí quản lý, phí bảo trì Sản phẩm phải có ngày cất nóc
        if self.bsd_loai_pt in ['pql', 'pbt']:
            if not self.bsd_unit_id.bsd_ngay_cn:
                raise UserError(_('Vui lòng kiểm tra thông tin sản phẩm trên hợp đồng.'))
        # ghi công nợ giảm
        giam_id = self.env['bsd.cong_no'].create({
                        'bsd_chung_tu': self.bsd_so_pt,
                        'bsd_ngay': time,
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
        # self.env['bsd.cong_no_ct'].create({
        #     'bsd_ngay_pb': time,
        #     'bsd_khach_hang_id': self.bsd_khach_hang_id.id,
        #     'bsd_phieu_thu_id': self.id,
        #     'bsd_hd_ban_id': self.bsd_hd_ban_id.id,
        #     'bsd_dot_tt_id': self.bsd_dot_tt_id.id,
        #     'bsd_tien_pb': self.bsd_tien,
        #     'bsd_loai': 'pt_dtt',
        #     'state': 'hieu_luc',
        # })

    # TC.01.08 - Kiểm tra thanh toán dư
    def _kiem_tra_tt_du(self):
        bsd_tien_tt_du = 0
        bsd_tien_tt = 0
        flag = False
        if self.bsd_loai_pt == 'tra_truoc':
            bsd_tien_tt = self.bsd_tien_kh
            bsd_tien_tt_du = 0
        if self.bsd_loai_pt == 'gc_tc' and self.bsd_gc_tc_id:
            cong_no_ct = self.env['bsd.cong_no_ct'].search([('bsd_gc_tc_id', '=', self.bsd_gc_tc_id.id)])
            if cong_no_ct:
                bsd_tien_phai_tt = self.bsd_gc_tc_id.bsd_tien_gc - sum(cong_no_ct.mapped('bsd_tien_pb'))
            else:
                bsd_tien_phai_tt = self.bsd_gc_tc_id.bsd_tien_gc
            if self.bsd_tien_kh > bsd_tien_phai_tt:
                flag = True
                bsd_tien_tt_du = self.bsd_tien_kh - bsd_tien_phai_tt
                bsd_tien_tt = bsd_tien_phai_tt
            else:
                bsd_tien_tt = self.bsd_tien_kh
        if self.bsd_loai_pt == 'giu_cho' and self.bsd_giu_cho_id:
            cong_no_ct = self.env['bsd.cong_no_ct'].search([('bsd_giu_cho_id', '=', self.bsd_giu_cho_id.id)])
            if cong_no_ct:
                bsd_tien_phai_tt = self.bsd_giu_cho_id.bsd_tien_gc - sum(cong_no_ct.mapped('bsd_tien_pb'))
            else:
                bsd_tien_phai_tt = self.bsd_giu_cho_id.bsd_tien_gc
            if self.bsd_tien_kh > bsd_tien_phai_tt:
                flag = True
                bsd_tien_tt_du = self.bsd_tien_kh - bsd_tien_phai_tt
                bsd_tien_tt = bsd_tien_phai_tt
            else:
                bsd_tien_tt = self.bsd_tien_kh
        if self.bsd_loai_pt == 'dat_coc' and self.bsd_dat_coc_id:
            cong_no_ct = self.env['bsd.cong_no_ct'].search([('bsd_dat_coc_id', '=', self.bsd_dat_coc_id.id),
                                                            ('bsd_dot_tt_id', '=', False)])
            if cong_no_ct:
                bsd_tien_phai_tt = self.bsd_dat_coc_id.bsd_tien_dc - sum(cong_no_ct.mapped('bsd_tien_pb'))
            else:
                bsd_tien_phai_tt = self.bsd_dat_coc_id.bsd_tien_dc
            if self.bsd_tien_kh > bsd_tien_phai_tt:
                flag = True
                bsd_tien_tt_du = self.bsd_tien_kh - bsd_tien_phai_tt
                bsd_tien_tt = bsd_tien_phai_tt
            else:
                bsd_tien_tt = self.bsd_tien_kh
        if self.bsd_loai_pt == 'hd' and self.bsd_dot_tt_id:
            cong_no_ct = self.env['bsd.cong_no_ct'].search([('bsd_dot_tt_id', '=', self.bsd_dot_tt_id.id)])
            tien_bg_dc = self.bsd_dot_tt_id.bsd_tien_dot_tt - self.bsd_dot_tt_id.bsd_tien_dc
            if cong_no_ct:
                bsd_tien_phai_tt = tien_bg_dc - sum(cong_no_ct.mapped('bsd_tien_pb'))
            else:
                bsd_tien_phai_tt = tien_bg_dc
            if self.bsd_tien_kh > bsd_tien_phai_tt:
                flag = True
                bsd_tien_tt_du = self.bsd_tien_kh - bsd_tien_phai_tt
                bsd_tien_tt = bsd_tien_phai_tt
            else:
                bsd_tien_tt = self.bsd_tien_kh
        return flag, bsd_tien_tt_du, bsd_tien_tt

    # TC.01.11 - Ghi sổ phiếu thu phí phát sinh
    def _gs_pt_pps(self, time):
        # Kiểm tra hợp đồng đã bị thanh lý chưa
        if self.bsd_hd_ban_id.state == 'thanh_ly':
            raise UserError(_('Hợp đồng đã bị thanh lý.\nVui lòng kiểm tra lại thông tin hợp đồng.'))
        self.env['bsd.cong_no'].create({
                'bsd_ngay': time,
                'bsd_khach_hang_id': self.bsd_khach_hang_id.id,
                'bsd_du_an_id': self.bsd_du_an_id.id,
                'bsd_ps_giam': self.bsd_tien,
                'bsd_ps_tang': 0,
                'bsd_loai_ct': 'phieu_thu',
                'bsd_phat_sinh': 'giam',
                'bsd_phieu_thu_id': self.id,
                'state': 'da_gs',
            })

    # TC.01.12 Cấn trừ công nợ phiếu thu
    def action_can_tru(self):    
        if self.bsd_hd_ban_id.state == 'thanh_ly':
            raise UserError(_('Hợp đồng đã bị thanh lý.\nVui lòng kiểm tra lại thông tin!'))
        list_ct = []
        if self.bsd_loai_pt == 'pps':
            if self.bsd_dot_tt_id:
                phi_ps_ids = self.env['bsd.phi_ps'].search([('bsd_dot_tt_id', '=', self.bsd_dot_tt_id.id)])
            elif self.bsd_hd_ban_id:
                phi_ps_ids = self.env['bsd.phi_ps'].search([('bsd_hd_ban_id', '=', self.bsd_hd_ban_id.id)])
            else:
                phi_ps_ids = []

            for phi_ps in phi_ps_ids:
                ct_can_tru = (0, 0, {
                                        'bsd_phi_ps_id': phi_ps.id,
                                        'bsd_dot_tt_id': phi_ps.bsd_dot_tt_id.id,
                                        'bsd_hd_ban_id': phi_ps.bsd_hd_ban_id.id,
                                        'bsd_so_ct': phi_ps.bsd_ma_ps,
                                        'bsd_loai_ct': 'pt_pps',
                                        'bsd_tien': phi_ps.bsd_tong_tien,
                                        'bsd_tien_phai_tt': phi_ps.bsd_tien_phai_tt,
                                    }
                              )
                list_ct.append(ct_can_tru)
        return {
            'type': 'ir.actions.act_window',
            'name': 'Cấn trừ công nợ',
            'res_model': 'bsd.can_tru',
            'view_mode': 'form',
            'target': 'current',
            'context': {'default_bsd_khach_hang_id': self.bsd_khach_hang_id.id,
                        'default_bsd_loai': 'pps',
                        'default_bsd_hd_ban_id': self.bsd_hd_ban_id.id,
                        'default_dot_tt_id': self.bsd_dot_tt_id.id,
                        'default_bsd_phieu_thu_id': self.id,
                        'default_bsd_ct_ids': list_ct
                        }
        }

    # Action in phiếu thu
    def action_in(self):
        return self.env.ref('bsd_tai_chinh.bsd_phieu_thu_report_action').read()[0]

    # Action hủy
    def action_huy(self):
        if self.state == 'nhap':
            self.write({'state': 'huy'})

    @api.model
    def create(self, vals):
        if 'bsd_du_an_id' in vals:
            du_an = self.env['bsd.du_an'].browse(vals['bsd_du_an_id'])
            sequence = du_an.get_ma_bo_cn(loai_cn=self._name)
        if not sequence:
            raise UserError(_('Dự án chưa có mã phiếu thu.'))
        vals['bsd_so_pt'] = sequence.next_by_id()
        return super(BsdPhieuThu, self).create(vals)

    # Tạo ra thanh toán trả trước khi thanh toán dư
    def tao_tt_tra_truoc(self, tien_du=0):
        tra_truoc = self.env['bsd.phieu_thu'].create({
                        'bsd_loai_pt': 'tra_truoc',
                        'bsd_khach_hang_id': self.bsd_khach_hang_id.id,
                        'bsd_du_an_id': self.bsd_du_an_id.id,
                        'bsd_pt_tt_id': self.bsd_pt_tt_id.id,
                        'bsd_tien_kh': tien_du,
                    }).action_xac_nhan()
        self.write({'bsd_tt_id': tra_truoc.id})
