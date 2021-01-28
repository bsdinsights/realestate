# -*- coding:utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError
import datetime
import logging
_logger = logging.getLogger(__name__)


class BsdHoanTien(models.Model):
    _name = 'bsd.hoan_tien'
    _description = 'Phiếu hoàn tiền khách hàng'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _rec_name = 'bsd_so_ct'

    bsd_so_ct = fields.Char(string="Số", help="Số chứng từ", required=True, readonly=True, copy=False,
                            default='/')
    _sql_constraints = [
        ('bsd_so_ct_unique', 'unique (bsd_so_ct)',
         'Số chứng từ hoàn tiền đã tồn tại !'),
    ]
    bsd_ngay_ct = fields.Date(string="Ngày", help="Ngày chứng từ", required=True,
                              default=lambda self: fields.Date.today(),
                              readonly=True,
                              states={'nhap': [('readonly', False)]})

    bsd_khach_hang_id = fields.Many2one('res.partner', string="Khách hàng", help="Khách hàng",
                                        required=True,
                                        readonly=True,
                                        states={'nhap': [('readonly', False)]})
    bsd_du_an_id = fields.Many2one('bsd.du_an', string="Dự án", help="Dự án", required=True,
                                   readonly=True,
                                   states={'nhap': [('readonly', False)]})
    bsd_tien = fields.Monetary(string="Tiền", help="Tiền", required=True,
                               readonly=True,
                               states={'nhap': [('readonly', False)]})
    bsd_dien_giai = fields.Char(string="Diễn giải", help="Diễn giải",
                                readonly=True,
                                states={'nhap': [('readonly', False)]})
    bsd_loai = fields.Selection(selection='_method_choice', string="Loại", help="Loại hoàn tiền",
                                default='phieu_thu',
                                readonly=True,
                                states={'nhap': [('readonly', False)]})
    bsd_pt_tt_id = fields.Many2one('bsd.pt_tt', string="Phương thức", help="Phương thức thanh toán",
                                   readonly=True,
                                   states={'nhap': [('readonly', False)]})
    bsd_chuyen_pt = fields.Boolean(string="Chuyển TT trả trước",
                                   help="Đánh dấu hoàn tiền có chuyển sang thanh toán trả trước hay không",
                                   readonly=True,
                                   states={'nhap': [('readonly', False)]})
    bsd_ngay_ht_tt = fields.Date(string="Ngày HT thực tế", help="Ngày hoàn tiền thực tế",
                                 readonly=True,
                                 states={'nhap': [('readonly', False)]})
    bsd_tk_nh_id = fields.Many2one('res.partner.bank', string="Tài khoản ngân hàng",
                                   help="Số tài khoản ngân hàng của khách hàng",
                                   readonly=True,
                                   states={'nhap': [('readonly', False)]})
    bsd_ngan_hang_id = fields.Many2one('res.bank', string="Tên ngân hàng", help="Tên ngân hàng",
                                       readonly=True,
                                       states={'nhap': [('readonly', False)]})

    @api.model
    def _method_choice(self):
        choices = [('gc_tc', 'Giữ chỗ thiện chí'),
                   ('giu_cho', 'Giữ chỗ'),
                   ('tl_dc', 'Thanh lý đặt cọc'),
                   ('phieu_thu', 'Thanh toán trả trước'),
                   ('tl_gd', 'Thanh lý giao dịch'),
                   ('vp_hd', 'Vi phạm hợp đồng'),
                   ('pl_hd', 'Phụ lục hợp đồng')]
        return choices

    bsd_phieu_thu_id = fields.Many2one('bsd.phieu_thu', string="Thanh toán trả trước", help="Thanh toán trả trước",
                                       readonly=True)
    bsd_gc_tc_id = fields.Many2one('bsd.gc_tc', string="Giữ chỗ thiện chí", help="Giữ chỗ thiện chí",
                                   readonly=True)
    bsd_giu_cho_id = fields.Many2one('bsd.giu_cho', string="Giữ chỗ", help="Giữ chỗ",
                                     readonly=True)
    bsd_dat_coc_id = fields.Many2one('bsd.dat_coc', string="Đặt cọc", help="Đặt cọc",
                                     readonly=True)
    bsd_hd_ban_id = fields.Many2one('bsd.hd_ban', string="Hợp đồng", help="Hợp đồng",
                                    readonly=True)
    bsd_vp_hd_id = fields.Many2one('bsd.vp_hd', string="Vi phạm HĐ", help="Vi phạm hợp đồng", readonly=True)
    bsd_thanh_ly_id = fields.Many2one('bsd.thanh_ly', string="Thanh lý", help="Thanh lý")

    state = fields.Selection([('nhap', 'Nháp'), ('xac_nhan', 'Xác nhận'),
                              ('huy', 'Hủy')], string="Trạng thái", tracking=1,
                             required=True, default='nhap')
    company_id = fields.Many2one('res.company', string='Công ty', default=lambda self: self.env.company)
    currency_id = fields.Many2one(related="company_id.currency_id", string="Tiền tệ", readonly=True)

    def action_tao(self):
        pass

    def action_xac_nhan(self):
        self.write({
            'state': 'xac_nhan',
        })

        # Cập nhật trạng thái hoàn tiền giữ chỗ thiện chí
        if self.bsd_loai == 'gc_tc':
            self.bsd_gc_tc_id.write({
                'bsd_tt_ht': 'da_ht'
            })
        # Cập nhật trạng thái hoàn tiền giữ chỗ
        if self.bsd_loai == 'giu_cho':
            self.bsd_giu_cho_id.write({
                'bsd_tt_ht': 'da_ht'
            })
        # Cập nhật trạng thái hoàn tiền thanh lý
        if self.bsd_thanh_ly_id:
            self.bsd_thanh_ly_id.write({
                'bsd_tt_ht': 'da_ht'
            })

        # Ghi sổ công nợ hoàn tiền
        self.env['bsd.cong_no'].create({
                'bsd_chung_tu': self.bsd_so_ct,
                'bsd_ngay': self.bsd_ngay_ct,
                'bsd_khach_hang_id': self.bsd_khach_hang_id.id,
                'bsd_du_an_id': self.bsd_du_an_id.id,
                'bsd_ps_giam': 0,
                'bsd_ps_tang': self.bsd_tien,
                'bsd_loai_ct': 'hoan_tien',
                'bsd_phat_sinh': 'tang',
                'bsd_hoan_tien_id': self.id,
                'state': 'da_gs',
            })

        # Tạo thanh toán trả trước
        if self.bsd_chuyen_pt:
            self.env['bsd.phieu_thu'].create({
                'bsd_loai_pt': 'tra_truoc',
                'bsd_khach_hang_id': self.bsd_khach_hang_id.id,
                'bsd_du_an_id': self.bsd_du_an_id.id,
                'bsd_pt_tt_id': self.env.ref('bsd_danh_muc.bsd_tien_mat').id,
                'bsd_tien_kh': self.bsd_tien,
            }).action_xac_nhan()

        # tạo record trong bảng công nợ chứng từ
        if self.bsd_loai == 'phieu_thu':
            ct = self.env['bsd.cong_no_ct'].create({
                    'bsd_ngay_pb': datetime.datetime.now(),
                    'bsd_khach_hang_id': self.bsd_khach_hang_id.id,
                    'bsd_phieu_thu_id': self.bsd_phieu_thu_id.id,
                    'bsd_hoan_tien_id': self.id,
                    'bsd_tien_pb': self.bsd_tien,
                    'bsd_loai': 'pt_ht',
                    'state': 'hieu_luc',
                })
            ct.kiem_tra_chung_tu()

    # TC.07.02 Hủy hoàn tiền
    def action_huy(self):
        self.write({
            'state': 'huy',
        })

    @api.model
    def create(self, vals):
        if 'bsd_du_an_id' in vals:
            du_an = self.env['bsd.du_an'].browse(vals['bsd_du_an_id'])
            sequence = du_an.get_ma_bo_cn(loai_cn=self._name)
        if not sequence:
            raise UserError(_('Dự án chưa có mã phiếu hoàn tiền.'))
        vals['bsd_so_ct'] = sequence.next_by_id()
        return super(BsdHoanTien, self).create(vals)

    # Action in phiếu thu
    def action_in(self):
        return self.env.ref('bsd_tai_chinh.bsd_hoan_tien_report_action').read()[0]
