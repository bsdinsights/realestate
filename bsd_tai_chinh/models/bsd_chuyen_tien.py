# -*- coding:utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError


class BsdChuyenTien(models.Model):
    _name = 'bsd.chuyen_tien'
    _description = 'Phiếu chuyển tiền khách hàng'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _rec_name = 'bsd_so_ct'

    bsd_so_ct = fields.Char(string="Số", help="Số chứng từ", required=True,
                            readonly=True, copy=False, default='/')
    _sql_constraints = [
        ('bsd_so_ct_unique', 'unique (bsd_so_ct)',
         'Số chứng từ chuyển tiền đã tồn tại !'),
    ]
    bsd_ngay_ct = fields.Datetime(string="Ngày", help="Ngày chứng từ", required=True,
                                  default=lambda self: fields.Datetime.now(),
                                  readonly=True,
                                  states={'nhap': [('readonly', False)]})

    bsd_nguoi_chuyen_id = fields.Many2one('res.partner', string="Chuyển từ", help="Thông tin người chuyển",
                                          required=True,
                                          readonly=True,
                                          states={'nhap': [('readonly', False)]})
    bsd_nguoi_nhan_id = fields.Many2one('res.partner', string="Chuyển đến", help="Thông tin người nhận",
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
    state = fields.Selection([('nhap', 'Nháp'), ('xac_nhan', 'Xác nhận'),
                              ('da_gs', 'Đã ghi sổ'), ('huy', 'Hủy')], string="Trạng thái", tracking=1,
                             required=True, default='nhap')
    company_id = fields.Many2one('res.company', string='Công ty', default=lambda self: self.env.company)
    currency_id = fields.Many2one(related="company_id.currency_id", string="Tiền tệ", readonly=True)

    # TC.05.01 Xác nhận chuyển tiền
    def action_xac_nhan(self):
        self.write({
            'state': 'xac_nhan',
        })

    # TC.05.03 Ghi sổ chuyển tiền
    def action_vao_so(self):
        self.write({
            'state': 'da_gs',
        })
        # Ghi sổ công nợ chuyển tiền
        self.env['bsd.cong_no'].create({
                'bsd_chung_tu': self.bsd_so_ct,
                'bsd_ngay': self.bsd_ngay_ct,
                'bsd_khach_hang_id': self.bsd_nguoi_chuyen_id.id,
                'bsd_du_an_id': self.bsd_du_an_id.id,
                'bsd_ps_giam': 0,
                'bsd_ps_tang': self.bsd_tien,
                'bsd_loai_ct': 'chuyen_tien',
                'bsd_phat_sinh': 'tang',
                'bsd_chuyen_tien_id': self.id,
                'state': 'da_gs',
            })
        # Tạo phiếu điều chỉnh giảm
        giam = self.env['bsd.giam_no'].create({
                'bsd_so_ct': self.bsd_so_ct,
                'bsd_ngay_ct': self.bsd_ngay_ct,
                'bsd_loai_dc': 'chuyen_tien',
                'bsd_dien_giai': "Chuyển tiền từ " + str(self.bsd_nguoi_chuyen_id.name),
                'bsd_khach_hang_id': self.bsd_nguoi_nhan_id.id,
                'bsd_du_an_id': self.bsd_du_an_id.id,
                'bsd_tien': self.bsd_tien,
                'state': 'xac_nhan',
        })
        # Tạo công nợ khách hàng
        giam.action_vao_so()

    # TC.05.02 Hủy chuyển tiền
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
            raise UserError(_('Dự án chưa có mã phiếu chuyển tiền'))
        vals['bsd_so_ct'] = sequence.next_by_id()
        return super(BsdChuyenTien, self).create(vals)