# -*- coding:utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError


class BsdGiamNo(models.Model):
    _name = 'bsd.giam_no'
    _description = 'Phiếu ghi giảm nợ khách hàng'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _rec_name = 'bsd_so_ct'

    bsd_so_ct = fields.Char(string="Số", help="Số chứng từ", required=True,
                            readonly=True, copy=False, default='/')
    _sql_constraints = [
        ('bsd_so_ct_unique', 'unique (bsd_so_ct)',
         'Số chứng từ giảm nợ đã tồn tại !'),
    ]
    bsd_ngay_ct = fields.Date(string="Ngày", help="Ngày chứng từ", required=True,
                              default=lambda self: fields.Date.today(),
                              readonly=True,
                              states={'nhap': [('readonly', False)]})
    bsd_loai_dc = fields.Selection(selection='_method_choice', string="Loại điều chỉnh", help="Loại điều chỉnh",
                                   readonly=True, default='khac',
                                   states={'nhap': [('readonly', False)]})

    @api.model
    def _method_choice(self):
        choices = [('khac', 'Điều chỉnh khác'),
                   ('huy_gctc', 'Hủy giữ chỗ thiện chí'),
                   ('huy_gc', 'Hủy giữ chỗ')]
        if self.env['res.users'].has_group('base.group_system'):
            choices += [('chuyen_tien', 'Chuyển tiền')]
        return choices
    bsd_dien_giai = fields.Char(string="Diễn giải", help="Lý do điều chỉnh",
                                readonly=True,
                                states={'nhap': [('readonly', False)]})
    bsd_khach_hang_id = fields.Many2one('res.partner', string="Khách hàng", help="Khách hàng", required=True,
                                        readonly=True,
                                        states={'nhap': [('readonly', False)]})
    bsd_du_an_id = fields.Many2one('bsd.du_an', string="Dự án", help="Dự án", required=True,
                                   readonly=True,
                                   states={'nhap': [('readonly', False)]})
    bsd_unit_id = fields.Many2one('product.product', string="Căn hộ", help="Căn hộ",
                                  readonly=True,
                                  states={'nhap': [('readonly', False)]})
    bsd_tien = fields.Monetary(string="Tiền", help="Tiền điều chỉnh", required=True,
                               readonly=True,
                               states={'nhap': [('readonly', False)]})
    bsd_tien_da_tt = fields.Monetary(string="Tiền đã thanh toán", help="Tiền đã thanh toán",
                                     compute='_compute_tien_ct', store=True)
    bsd_tien_con_lai = fields.Monetary(string="Tiền còn lại", help="Tiền còn lại",
                                       compute='_compute_tien_ct', store=True)
    bsd_ct_ids = fields.One2many('bsd.cong_no_ct', 'bsd_giam_no_id', string="Công nợ chứng tự", readonly=True)

    @api.depends('bsd_ct_ids', 'bsd_ct_ids.bsd_tien_pb', 'bsd_tien')
    def _compute_tien_ct(self):
        for each in self:
            each.bsd_tien_da_tt = sum(each.bsd_ct_ids.mapped('bsd_tien_pb'))
            each.bsd_tien_con_lai = each.bsd_tien - each.bsd_tien_da_tt

    state = fields.Selection([('nhap', 'Nháp'), ('xac_nhan', 'Xác nhận'),
                              ('da_gs', 'Đã ghi sổ'), ('huy', 'Hủy')], string="Trạng thái", tracking=1,
                             required=True, default='nhap')
    company_id = fields.Many2one('res.company', string='Công ty', default=lambda self: self.env.company)
    currency_id = fields.Many2one(related="company_id.currency_id", string="Tiền tệ", readonly=True)

    # TC.08.01 Xác nhận điều chỉnh giảm
    def action_xac_nhan(self):
        self.write({
            'state': 'xac_nhan',
        })

    # TC.08.03 Ghi sổ điều chỉnh
    def action_vao_so(self):
        self.write({
            'state': 'da_gs',
        })
        self.env['bsd.cong_no'].create({
                'bsd_chung_tu': self.bsd_so_ct,
                'bsd_ngay': self.bsd_ngay_ct,
                'bsd_khach_hang_id': self.bsd_khach_hang_id.id,
                'bsd_du_an_id': self.bsd_du_an_id.id,
                'bsd_ps_giam': self.bsd_tien,
                'bsd_ps_tang': 0,
                'bsd_loai_ct': 'dc_giam',
                'bsd_phat_sinh': 'giam',
                'bsd_giam_no_id': self.id,
                'state': 'da_gs',
            })

    # TC.08.02 Hủy điều chỉnh
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
            raise UserError(_('Dự án chưa có mã phiếu điều chỉnh giảm'))
        vals['bsd_so_ct'] = sequence.next_by_id()
        return super(BsdGiamNo, self).create(vals)