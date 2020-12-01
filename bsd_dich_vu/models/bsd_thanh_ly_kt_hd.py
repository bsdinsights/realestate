# -*- coding:utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError
import logging
_logger = logging.getLogger(__name__)


class BsdThanhLyKetThucHopDong(models.Model):
    _name = 'bsd.tl_kt_hd'
    _description = "Thanh lý kết thúc hơp đồng"
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _rec_name = 'bsd_ma'

    bsd_ma = fields.Char(string="Mã", help="Mã thanh lý kết thúc hợp đồng", required=True, readonly=True,
                         copy=False, default='/')
    _sql_constraints = [
        ('bsd_ma_unique', 'unique (bsd_ma)',
         'Mã thanh lý kết thúc hợp đồng đã tồn tại !')
    ]
    bsd_ngay_tao = fields.Datetime(string="Ngày", help="Ngày thanh lý kết thúc hợp đồng",
                                   required=True, default=lambda self: fields.Datetime.now(),
                                   readonly=True,
                                   states={'nhap': [('readonly', False)]})
    bsd_ten = fields.Char(string="Tiêu đề", required=True, help="Tiêu đề thanh lý kết thúc hợp đồng",
                          readonly=True,
                          states={'nhap': [('readonly', False)]})
    bsd_loai = fields.Selection([('gui_thu', 'Gửi thư'), ('dat_bh', 'Đặt buổi hẹn')], string="Hình thức TLHĐ",
                                help="Hình thức được chọn để thực hiện thanh lý hợp đồng", required=True,
                                default='gui_thu')
    bsd_du_an_id = fields.Many2one('bsd.du_an', string="Dự án", help="Dự án", required=True)
    bsd_hd_ban_id = fields.Many2one('bsd.hd_ban', string="Hợp đồng", help="Hợp đồng", required=True)
    bsd_unit_id = fields.Many2one('product.product', string="Sản phẩm", help="Sản phẩm", required=True)
    bsd_khach_hang_id = fields.Many2one('res.partner', string="Khách hàng", help="Khách hàng", required=True)
    bsd_bg_gt_id = fields.Many2one('bsd.bg_gt', string="Bàn giao giấy tờ", help="Bàn giao giấy tờ", required=True)
    bsd_han_th = fields.Date(string="Hạn thu hồi", help="Thời hạn thu hồi Biên bản thanh lý kết thúc hợp đồng",
                             readonly=True,
                             states={'nhap': [('readonly', False)]})
    bsd_ngay_in = fields.Datetime(string="Ngày in", help="Ngày in Biên bản thanh lý kết thúc hợp đồng",
                                  readonly=True)
    bsd_nguoi_in_id = fields.Many2one('res.users', string="Người in", readonly=True,
                                      help="Người in biên bản thanh lý kết thúc hợp đồng")
    bsd_ngay_xn = fields.Datetime(string="Ngày xác nhận", readonly=True,
                                  help="Ngày xác nhận ký biên bản")
    bsd_nguoi_xn_id = fields.Many2one('res.users', string="Người xác nhận ký", readonly=True,
                                      help="Người xác nhận ký biên bản thanh lý kết thúc hợp đồng")
    company_id = fields.Many2one('res.company', string='Công ty', default=lambda self: self.env.company)
    currency_id = fields.Many2one(related="company_id.currency_id", string="Tiền tệ", readonly=True)
    state = fields.Selection([('nhap', 'Nháp'),
                              ('xac_nhan', 'Xác nhận'),
                              ('da_tl', 'Hoàn thành'),
                              ('huy', 'Hủy')],
                             string="Trạng thái", default="nhap", required=True, readonly=True, tracking=1)

    @api.onchange('bsd_hd_ban_id')
    def _onchange_hd_ban(self):
        self.bsd_unit_id = self.bsd_hd_ban_id.bsd_unit_id
        self.bsd_khach_hang_id = self.bsd_hd_ban_id.bsd_khach_hang_id

    @api.onchange('bsd_unit_id')
    def _onchange_unit(self):
        self.bsd_bg_gt_id = self.bsd_unit_id.bsd_bg_gt_id

    # DV.14.01 Xác nhận thanh lý kết thúc hợp đồng
    def action_xac_nhan(self):
        if self.state == 'nhap':
            self.write({
                'state': 'xac_nhan',
            })

    # DV.14.02 In thanh lý kết thúc hợp đồng
    def action_in(self):
        action = self.env.ref('bsd_dich_vu.bsd_tl_kt_hd_report_action').read()[0]
        return action

    # DV.14.03 Ký thanh lý kết thúc hợp đồng
    def action_ky(self):
        action = self.env.ref('bsd_dich_vu.bsd_wizard_ky_tl_kt_hd_action').read()[0]
        return action

    # DV.14.04 Hủy thanh lý kết thúc hợp đồng
    def action_huy(self):
        if self.state in ['nhap', 'xac_nhan']:
            self.write({
                'state': 'huy'
            })

    @api.model
    def create(self, vals):
        sequence = self.env['ir.sequence']
        if 'bsd_du_an_id' in vals:
            du_an = self.env['bsd.du_an'].browse(vals['bsd_du_an_id'])
            sequence = du_an.get_ma_bo_cn(loai_cn=self._name)
        if not sequence:
            raise UserError(_('Dự án chưa có mã thanh lý kết thúc hợp đồng.'))
        vals['bsd_ma'] = sequence.next_by_id()
        return super(BsdThanhLyKetThucHopDong, self).create(vals)
