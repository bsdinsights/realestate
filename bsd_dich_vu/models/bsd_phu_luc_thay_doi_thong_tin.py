# -*- coding:utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError
import datetime
import logging
_logger = logging.getLogger(__name__)


class BsdPLTDTT(models.Model):
    _name = 'bsd.pl_tti'
    _description = "Phụ lục thay đổi thông tin"
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _rec_name = 'bsd_ma'

    bsd_ma = fields.Char(string="Mã", help="Mã phụ lục hợp đồng thay đổi thông tin",
                         required=True, readonly=True,
                         copy=False, default='/')
    _sql_constraints = [
        ('bsd_ma_unique', 'unique (bsd_ma)',
         'Mã phụ lục hợp đồng đã tồn tại !'),
    ]
    bsd_ngay = fields.Date(string="Ngày", help="Ngày tạo phụ lục hợp đồng", required=True,
                           default=lambda self: fields.Datetime.now(),
                           readonly=True,
                           states={'nhap': [('readonly', False)]})
    bsd_khach_hang_id = fields.Many2one('res.partner', string="Khách hàng", help="Tên khách hàng", required=True,
                                        readonly=True,
                                        states={'nhap': [('readonly', False)]})
    bsd_hd_ban_id = fields.Many2one('bsd.hd_ban', string="Hợp đồng", help="Hợp đồng mua bán", required=True,
                                    readonly=True,
                                    states={'nhap': [('readonly', False)]})
    bsd_du_an_id = fields.Many2one(string="Dự án", help="Tên dự án", related='bsd_hd_ban_id.bsd_du_an_id', store=True)
    bsd_unit_id = fields.Many2one(string="Sản phẩm", help="Tên Sản phẩm", related='bsd_hd_ban_id.bsd_unit_id', store=True)
    bsd_dien_giai = fields.Char(string="Diễn giải", help="Diễn giải",
                                readonly=True,
                                states={'nhap': [('readonly', False)]})
    state = fields.Selection([('nhap', 'Nháp'), ('xac_nhan', 'Xác nhận'),
                              ('dk_pl', 'Đã ký phụ lục'), ('huy', 'Hủy')],
                             string="Trạng thái", help="Trạng thái", required=True, default="nhap", tracking=1)
    bsd_loai_pl = fields.Selection([('dien_tich', 'Diện tích'), ('ten_ch', 'Tên Sản phẩm')], required=True,
                                   string="Loại thay đổi", help="Loại phụ lục hợp đồng", default="dien_tich",
                                   readonly=True,
                                   states={'nhap': [('readonly', False)]})
    bsd_cn_dttt_unit_id = fields.Many2one('bsd.cn_dttt_unit', string="CN.DTTT chi tiết",
                                          help="Chi tiết cập nhật diện tích thông thủy thực tế của sản phẩm",
                                          readonly=True)
    bsd_dt_tt_tt = fields.Float(string="DT thực tế", help="Diện tích thông thủy thực tế",
                                readonly=True)
    bsd_dt_tt_tk = fields.Float(string="DT thiết kế",
                                help="Diện tích thông thủy thiết kế", readonly=True)
    bsd_cl_tt = fields.Float(string="CL thực tế", help="Phầm trăm chênh lệch thực tế sau khi đo đạt",
                             readonly=True, digits=(2, 2))
    bsd_cl_cp = fields.Float(string="CL cho phép", help="Phần trăm chênh lệch cho phép của sản phẩm",
                             readonly=True)

    bsd_ten_unit_moi = fields.Char(string="Tên sản phẩm (mới)", help="Tên Sản phẩm mới",
                                   readonly=True,
                                   states={'nhap': [('readonly', False)]})
    bsd_ten_unit_cu = fields.Char(string="Tên sản phẩm (cũ)", help="Tên Sản phẩm (cũ) trước khi được thay đổi",
                                  readonly=True)
    bsd_ngay_ky_pl = fields.Date(string="Ngày ký PL", help="Ngày ký phụ lục hợp đồng", readonly=True)
    bsd_nguoi_xn_ky_id = fields.Many2one('res.users', string="Người xn ký",
                                         help="Người xác nhận ký phụ lục hợp đồng", readonly=True)

    bsd_ngay_duyet = fields.Date(string="Ngày duyệt", help="Ngày duyệt phụ lục hợp đồng", readonly=True)
    bsd_nguoi_duyet_id = fields.Many2one('res.users', string="Người duyệt", readonly=True)
    bsd_nguoi_xn_id = fields.Many2one('res.users', string="Người xác nhận", readonly=True)
    bsd_ngay_xn = fields.Date(string="Ngày xác nhận", help="Ngày xác nhận phụ lục hợp đồng", readonly=True)
    bsd_nguoi_huy_id = fields.Many2one('res.users', string="Người hủy", readonly=True)
    bsd_ngay_huy = fields.Date(string="Ngày hủy", help="Ngày hủy phụ lục hợp đồng", readonly=True)
    bsd_ly_do_huy = fields.Char(string="Lý do hủy", help="Lý do hủy phụ lục", readonly=True)
    bsd_ly_do = fields.Char(string="Lý do không duyệt", readonly=True, tracking=2)

    # DV.03.01 - Xác nhận phụ lục hợp đồng
    def action_xac_nhan(self):
        self.write({
            'state': 'xac_nhan',
        })

    # DV.03.02 - Ký phụ lục hợp đồng
    def action_ky_pl(self):
        action = self.env.ref('bsd_dich_vu.bsd_wizard_ky_pl_tti_action').read()[0]
        return action

    # DV.03.03 - Hủy phụ lục hợp đồng
    def action_huy(self):
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
            raise UserError(_('Dự án chưa có quy định mã phụ lục thay đổi giá trị QSDĐ.\n'
                              'Vui lòng kiểm tra lại thông tin.'))
        vals['bsd_ma'] = sequence.next_by_id()
        res = super(BsdPLTDTT, self).create(vals)
