# -*- coding:utf-8 -*-

from odoo import models, fields, api
from odoo.exceptions import UserError
import logging
_logger = logging.getLogger(__name__)


class BsdHoanTien(models.Model):
    _name = 'bsd.hoan_tien'
    _description = 'Phiếu hoàn tiền khách hàng'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _rec_name = 'bsd_so_ct'

    bsd_so_ct = fields.Char(string="Số", help="Số chứng từ", required=True,
                            readonly=True,
                            states={'nhap': [('readonly', False)]})
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
    bsd_loai = fields.Selection([('phieu_thu', 'Phiếu thu')], string="Loại", help="Loại hoàn tiền", required=True,
                                default='phieu_thu',
                                readonly=True,
                                states={'nhap': [('readonly', False)]})
    bsd_phieu_thu_id = fields.Many2one('bsd.phieu_thu', string="Phiếu thu", help="Phiếu thu", required=True,
                                       readonly=True,
                                       states={'nhap': [('readonly', False)]})
    bsd_tien_con_lai = fields.Monetary(related="bsd_phieu_thu_id.bsd_tien_con_lai")
    state = fields.Selection([('nhap', 'Nháp'), ('xac_nhan', 'Xác nhận'),
                              ('da_gs', 'Đã ghi sổ'), ('huy', 'Hủy')], string="Trạng thái", tracking=1,
                             required=True, default='nhap')
    company_id = fields.Many2one('res.company', string='Công ty', default=lambda self: self.env.company)
    currency_id = fields.Many2one(related="company_id.currency_id", string="Tiền tệ", readonly=True)

    @api.constrains('bsd_tien')
    def _constrains_tien(self):
        if self.bsd_tien > self.bsd_tien_con_lai:
            raise UserError("Tiền hoàn lại vượt quá số tiền còn lại. Vui lòng kiểm tra lại!")

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
        self.env['bsd.cong_no_ct'].create({
            'bsd_ngay_pb': self.bsd_ngay_ct,
            'bsd_khach_hang_id': self.bsd_khach_hang_id.id,
            'bsd_phieu_thu_id': self.bsd_phieu_thu_id.id,
            'bsd_hoan_tien_id': self.id,
            'bsd_tien_pb': self.bsd_tien,
            'bsd_loai': 'pt_ht',
            'state': 'hoan_thanh'
        })

    # TC.07.02 Hủy hoàn tiền
    def action_huy(self):
        self.write({
            'state': 'huy',
        })