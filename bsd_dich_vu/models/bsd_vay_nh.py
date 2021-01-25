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
                           readonly=True,
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
    bsd_tien_vay = fields.Monetary(string="Số tiền vay", help="Số tiền vay ngân hàng", required=True,
                                   readonly=True,
                                   states={'nhap': [('readonly', False)]})
    bsd_so_nam_vay = fields.Integer(string="Số năm vay", help="Số năm vay ngân hàng", required=True,
                                    readonly=True,
                                    states={'nhap': [('readonly', False)]})
    bsd_lai_suat = fields.Float(string="Lãi suất", help="Lãi suất vay ngân hàng", required=True,
                                readonly=True,
                                states={'nhap': [('readonly', False)]})
    state = fields.Selection([('nhap', 'Nháp'),
                              ('xac_nhan', 'Xác nhận'),
                              ('da_tc', 'Đã thế chấp'),
                              ('da_gc', 'Đã giải chấp'),
                              ('huy', 'Hủy')],
                             string="Trạng thái", default="nhap", required=True, readonly=True, tracking=1)
    bsd_ly_do = fields.Char(string="Lý do", readonly=True, tracking=2)
    company_id = fields.Many2one('res.company', string='Công ty', default=lambda self: self.env.company)
    currency_id = fields.Many2one(related="company_id.currency_id", string="Tiền tệ", readonly=True)
    bsd_ngay_xn = fields.Date(string='Ngày xác nhận', help="Ngày xác nhận yêu cầu vay thế chấp của ngân hàng",
                              readonly=True)
    bsd_nguoi_xn_id = fields.Many2one('res.users', string="Người xác nhận",
                                      help="Người xác nhận yêu cần vay của khách hàng", readonly=True)
    bsd_ngay_tc = fields.Date(string='Ngày duyệt thế chấp', help="Ngày duyệt thế chấp ngân hàng", readonly=True)
    bsd_nguoi_tc_id = fields.Many2one('res.users', string="Người duyệt thế chấp",
                                            help="Người duyệt thế chấp ngân hàng", readonly=True)
    bsd_ngay_gc = fields.Date(string='Ngày duyệt giải chấp', help="Ngày duyệt giải chấp ngân hàng", readonly=True)
    bsd_nguoi_gc_id = fields.Many2one('res.users', string="Người duyệt giải chấp",
                                            help="Người duyệt giải chấp ngân hàng", readonly=True)

    @api.constrains('bsd_hd_ban_id')
    def _constrains_hd(self):
        # Kiểm tra hợp đồng đã ký và chưa thanh lý
        if not self.bsd_hd_ban_id.bsd_ngay_ky_hdb:
            raise UserError(_("Hợp đồng chưa ký. Vui lòng kiểm tra lại thông tin."))
        if self.bsd_hd_ban_id.state == '12_thanh_ly':
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
        chuyen_nhuong = self.env['bsd.hd_ban_cn'].search([('bsd_hd_ban_id', '=', self.bsd_hd_ban_id.id),
                                                         ('state', 'not in', ['huy', 'duyet'])])
        if chuyen_nhuong:
            raise UserError(_("Hợp đồng đang chuyển nhượng. Vui lòng kiểm tra lại thông tin."))
        # Kiểm tra hợp đồng có phụ lục đồng sở hữu nào đang có hiệu lực hay ko
        pl_dsh = self.env['bsd.pl_dsh'].search([('bsd_hd_ban_id', '=', self.bsd_hd_ban_id.id),
                                                ('state', 'not in', ['huy', 'dk_pl'])])
        if pl_dsh:
            raise UserError(_("Hợp đồng đang có phụ lục thay đổi đồng sở hữu. Vui lòng kiểm tra lại thông tin."))

    def action_xac_nhan(self):
        # kiểm tra hợp đồng
        self._constrains_hd()
        if self.state == 'nhap':
            self.write({
                'state': 'xac_nhan',
                'bsd_ngay_xn': fields.Date.today(),
                'bsd_nguoi_xn_id': self.env.uid,
            })
        # Cập nhật trạng thái tình trạng vay của sản phẩm
        self.bsd_unit_id.write({
            'bsd_tt_vay': '1'
        })

    def action_the_chap(self):
        if self.state == 'xac_nhan':
            self.write({
                'state': 'da_tc',
                'bsd_nguoi_tc_id': self.env.uid,
                'bsd_ngay_tc': fields.Date.today()
            })

    def action_giai_chap(self):
        if self.state == 'da_tc':
            self.write({
                'state': 'da_gc',
                'bsd_nguoi_gc_id': self.env.uid,
                'bsd_ngay_gc': fields.Date.today()
            })
        # Cập nhật trạng thái tình trạng vay của sản phẩm
        self.bsd_unit_id.write({
            'bsd_tt_vay': '0'
        })

    def action_huy(self):
        if self.state in ['nhap', 'xac_nhan']:
            self.write({
                'state': 'huy',
            })

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
