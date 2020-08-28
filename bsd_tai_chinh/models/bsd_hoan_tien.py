# -*- coding:utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError
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
    bsd_ngay_ct = fields.Datetime(string="Ngày", help="Ngày chứng từ", required=True,
                                  default=lambda self: fields.Datetime.now(),
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

    @api.model
    def _method_choice(self):
        choices = [('phieu_thu', 'Phiếu thu'),
                   ('gd_ck', 'Giao dịch chiết khấu'),
                   ('tl_dc', 'Thanh lý đặt cọc'),
                   ('tl_dc_hd', 'Thanh lý đặt cọc - Chuẩn bị HĐ'),
                   ('tl_ttdc', 'Thanh lý TTĐC'),
                   ('tl_hd', 'Thanh lý hợp đồng')]
        if self.env['res.users'].has_group('base.group_system'):
            choices += [('dc_giam', 'Điều chỉnh giảm')]
        return choices

    bsd_phieu_thu_id = fields.Many2one('bsd.phieu_thu', string="Phiếu thu", help="Phiếu thu",
                                       readonly=True,
                                       states={'nhap': [('readonly', False)]})
    bsd_giam_no_id = fields.Many2one('bsd.giam_no', string="Điều chỉnh giảm", help="Điều chỉnh giảm",
                                     readonly=True,
                                     states={'nhap': [('readonly', False)]})
    bsd_ps_gd_ck_id = fields.Many2one('bsd.ps_gd_ck', string="Giao dịch chiết khấu", help="Giao dịch chiết khấu",
                                      readonly=True,
                                      states={'nhap': [('readonly', False)]})
    bsd_thanh_ly_id = fields.Many2one('bsd.thanh_ly', string="Thanh lý", help="Thanh lý")
    state = fields.Selection([('nhap', 'Nháp'), ('xac_nhan', 'Xác nhận'),
                              ('da_gs', 'Đã ghi sổ'), ('huy', 'Hủy')], string="Trạng thái", tracking=1,
                             required=True, default='nhap')
    company_id = fields.Many2one('res.company', string='Công ty', default=lambda self: self.env.company)
    currency_id = fields.Many2one(related="company_id.currency_id", string="Tiền tệ", readonly=True)

    # TC.07.01 Xác nhận hoàn tiền
    def action_xac_nhan(self):
        self.write({
            'state': 'xac_nhan',
        })

    # TC.07.03 Ghi sổ hoàn tiền
    def action_vao_so(self):
        self.write({
            'state': 'da_gs',
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
        # tạo record trong bảng công nợ chứng từ
        if self.bsd_loai == 'phieu_thu':
            self.env['bsd.cong_no_ct'].create({
                'bsd_ngay_pb': self.bsd_ngay_ct,
                'bsd_khach_hang_id': self.bsd_khach_hang_id.id,
                'bsd_phieu_thu_id': self.bsd_phieu_thu_id.id,
                'bsd_hoan_tien_id': self.id,
                'bsd_tien_pb': self.bsd_tien,
                'bsd_loai': 'pt_ht',
                'state': 'hoan_thanh'
            })
        elif self.bsd_loai == 'dc_giam':
            self.env['bsd.cong_no_ct'].create({
                'bsd_ngay_pb': self.bsd_ngay_ct,
                'bsd_khach_hang_id': self.bsd_khach_hang_id.id,
                'bsd_giam_no_id': self.bsd_giam_no_id.id,
                'bsd_hoan_tien_id': self.id,
                'bsd_tien_pb': self.bsd_tien,
                'bsd_loai': 'giam_ht',
                'state': 'hoan_thanh'
            })

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
            raise UserError(_('Dự án chưa có mã phiếu hoàn tiền'))
        vals['bsd_so_ct'] = sequence.next_by_id()
        return super(BsdHoanTien, self).create(vals)
