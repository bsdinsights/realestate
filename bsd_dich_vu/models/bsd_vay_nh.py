# -*- coding:utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError
import logging
_logger = logging.getLogger(__name__)


class BsdVayNganHang(models.Model):
    _name = 'bsd.vay_nh'
    _description = "Quy trình vay ngân hàng"
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _rec_name = 'bsd_ma'

    bsd_ma = fields.Char(string="Mã", help="Mã vay ngân hàng của khách hàng", required=True, readonly=True,
                         copy=False, default='/')
    _sql_constraints = [
        ('bsd_ma_unique', 'unique (bsd_ma)',
         'Mã yêu cầu vay ngân hàng đã tồn tại !')
    ]
    bsd_ngay = fields.Date(string="Ngày", help="Ngày tạo yêu cầu vay ngân hàng của khách hàng",
                           required=True, default=lambda self: fields.Date.today(),
                           eadonly=True,
                           states={'nhap': [('readonly', False)]})
    bsd_ten = fields.Char(string="Tiêu đề", required=True, help="Tiêu đề",
                          readonly=True,
                          states={'nhap': [('readonly', False)]})
    bsd_du_an_id = fields.Many2one('bsd.du_an', string="Dự án", help="Dự án", required=True,
                                   readonly=True,
                                   states={'nhap': [('readonly', False)]})
    bsd_hd_ban_id = fields.Many2one('bsd.hd_ban', string="Hợp đồng", help="Hợp đồng", required=True,
                                    readonly=True,
                                    states={'nhap': [('readonly', False)]})

    @api.onchange('bsd_hd_ban_id')
    def _onchange_hd(self):
        self.bsd_unit_id = self.bsd_hd_ban_id.bsd_unit_id

    bsd_unit_id = fields.Many2one('product.product', string="Sản phẩm", help="Sản phẩm", required=True,
                                  readonly=True,
                                  states={'nhap': [('readonly', False)]})
    bsd_khach_hang_id = fields.Many2one('res.partner', string="Khách hàng", help="Khách hàng", required=True,
                                        readonly=True,
                                        states={'nhap': [('readonly', False)]})
    bsd_ngan_hang_id = fields.Many2one('res.bank', string="Ngân hàng", help="Ngân hàng cho vay của dự án",
                                       required=True,
                                       readonly=True,
                                       states={'nhap': [('readonly', False)]})
    bsd_tien_vay = fields.Monetary(string="Số tiền vay", help="Số tiền vay ngân hàng", required=True)
    bsd_so_nam_vay = fields.Integer(string="Số năm vay", help="Số năm vay ngân hàng", required=True)
    bsd_lai_suat = fields.Float(string="Lãi suất", help="Lãi suất vay ngân hàng", required=True)
    state = fields.Selection([('nhap', 'Nháp'),
                              ('xac_nhan', 'Xác nhận'),
                              ('huy', 'Hủy')],
                             string="Trạng thái", default="nhap", required=True, readonly=True, tracking=1)
    bsd_ly_do = fields.Char(string="Lý do", readonly=True, tracking=2)
    company_id = fields.Many2one('res.company', string='Công ty', default=lambda self: self.env.company)
    currency_id = fields.Many2one(related="company_id.currency_id", string="Tiền tệ", readonly=True)

    @api.constrains('bsd_hd_ban_id')
    def _constrains_hd(self):
        # Kiểm tra hợp đồng đã ký và chưa thanh lý
        if not self.bsd_hd_ban_id.bsd_ngay_ky_hdb:
            raise UserError(_("Hợp đồng chưa ký. Vui lòng kiểm tra lại thông tin."))
        if self.bsd_hd_ban_id.state == 'thanh_ly':
            raise UserError(_("Hợp đồng đã thanh lý. Vui lòng kiểm tra lại thông tin."))
        # Kiểm tra hợp đồng đã vay ngân hàng chưa
        if self.bsd_hd_ban_id.bsd_unit_id.bsd_tt_vay == '1':
            raise UserError(_("Hợp đồng đã vay ngân hàng. Vui lòng kiểm tra lại thông tin."))
        # Kiểm tra hợp đồng có đang bị thanh lý hay ko
        thanh_ly = self.env['bsd.thanh_ly'].search([('bsd_hd_ban_id', '=', self.bsd_hd_ban_id.id),
                                                    ('state', '!=', 'huy')])
        if thanh_ly:
            raise UserError(_("Hợp đồng đang thanh lý. Vui lòng kiểm tra lại thông tin."))
        # Kiểm tra hợp đồng có đang chuyển nhượng hay ko
        chuyen_nhuong = self.env['bsd.hd_ban_cn'].search([('bsd_hd_ban_id', '=', self.bsd_hd_ban_id.id)],
                                                         ('state', 'not in', ['huy', 'duyet']))
        if chuyen_nhuong:
            raise UserError(_("Hợp đồng đang chuyển nhượng. Vui lòng kiểm tra lại thông tin."))
        # Kiểm tra hợp đồng có phụ lục đồng sở hữu nào đang có hiệu lực hay ko
        pl_dsh = self.env['bsd.pl_dsh'].search([('bsd_hd_ban_id', '=', self.bsd_hd_ban_id.id)],
                                                ('state', 'not in', ['huy', 'dk_pl']))
        if pl_dsh:
            raise UserError(_("Hợp đồng đang có phụ lục thay đổi đồng sở hữu. Vui lòng kiểm tra lại thông tin."))

    @api.model
    def create(self, vals):
        sequence = self.env['ir.sequence']
        if 'bsd_du_an_id' in vals:
            du_an = self.env['bsd.du_an'].browse(vals['bsd_du_an_id'])
            sequence = du_an.get_ma_bo_cn(loai_cn=self._name)
        if not sequence:
            raise UserError(_('Dự án chưa có mã yêu cầu vay ngân hàng.'))
        vals['bsd_ma'] = sequence.next_by_id()
        return super(BsdVayNganHang, self).create(vals)
