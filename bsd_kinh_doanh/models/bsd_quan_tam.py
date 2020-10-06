# -*- coding:utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError
import datetime
import logging

_logger = logging.getLogger(__name__)


class BsdQuanTam(models.Model):
    _name = 'bsd.quan_tam'
    _description = "Thông tin quan tâm"
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _rec_name = 'bsd_khach_hang_id'

    bsd_ngay_qt = fields.Datetime(string="Ngày quan tâm", required=True, default=lambda self: fields.Datetime.now(),
                                  readonly=True, help='Ngày quan tâm',
                                  states={'nhap': [('readonly', False)]})
    bsd_ngay_hh_qt = fields.Datetime(string="Ngày hết hạn", readonly=True)
    bsd_khach_hang_id = fields.Many2one('res.partner', string="Khách hàng", required=True,
                                        readonly=True, help="Tên khách hàng",
                                        states={'nhap': [('readonly', False)]})
    bsd_du_an_id = fields.Many2one('bsd.du_an', string="Dự án", required=True,
                                   readonly=True, help="Tên dự án",
                                   states={'nhap': [('readonly', False)]})
    bsd_unit_id = fields.Many2one('product.product', string="Sản phẩm", required=True,
                                  readonly=True, help="Tên Sản phẩm",
                                  states={'nhap': [('readonly', False)]})
    bsd_ten_sp = fields.Char(related="bsd_unit_id.name")
    bsd_product_tmpl_id = fields.Many2one(related='bsd_unit_id.product_tmpl_id', store=True)
    bsd_dien_giai = fields.Char(string="Diễn giải",
                                readonly=True, help="Diễn giải",
                                states={'nhap': [('readonly', False)]})

    def _get_nhan_vien(self):
        return self.env['hr.employee'].search([('user_id', '=', self.env.uid)])

    bsd_nvbh_id = fields.Many2one('hr.employee', string="Nhân viên KD", help="Nhân viên kinh doanh",
                                  readonly=True, required=True, default=_get_nhan_vien,
                                  states={'nhap': [('readonly', False)]})

    state = fields.Selection([('nhap', 'Nháp'),
                              ('xac_nhan', 'Xác nhận'),
                              ('het_han', 'Hết hạn')], default='nhap', string="Trạng thái",
                             tracking=1, help="Trạng thái", required=True, readonly=True)

    def action_xac_nhan(self):
        self.write({
            'state': 'xac_nhan',
            'bsd_ngay_qt': fields.Datetime.now(),
            'bsd_ngay_hh_qt': fields.Datetime.now() + datetime.timedelta(hours=self.bsd_du_an_id.bsd_hh_qt)
        })

    def auto_huy_qt(self):
        self.write({
            'state': 'het_han'
        })

    @api.constrains('bsd_khach_hang_id','bsd_unit_id')
    def _constraint_kh(self):
        quan_tam = self.search([('bsd_khach_hang_id', '=', self.bsd_khach_hang_id.id),
                                ('bsd_unit_id', '=', self.bsd_unit_id.id),
                                ('id', '!=', self.id), ('state', '=', 'xac_nhan')])
        if quan_tam:
            raise UserError(_("Khách hàng đã quan tâm sảm phẩm này.\n Vui lòng kiểm tra lại thông tin."))
