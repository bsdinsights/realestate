# -*- coding:utf-8 -*-

from odoo import models, fields, api
import datetime
import logging
_logger = logging.getLogger(__name__)


class BsdPLTDTT(models.Model):
    _name = 'bsd.pl_tti'
    _description = "Phụ lục thay đổi thông tin"
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _rec_name = 'bsd_ma_pl_tti'

    bsd_ma_pl_tti = fields.Char(string="Mã", help="Mã phụ lục hợp đồng thay đổi thông tin", required=True,
                                readonly=True,
                                states={'nhap': [('readonly', False)]})
    _sql_constraints = [
        ('bsd_ma_pl_tti_unique', 'unique (bsd_ma_pl_tti)',
         'Mã phụ lục hợp đồng đã tồn tại !'),
    ]
    bsd_ngay_pl_tti = fields.Datetime(string="Ngày", help="Ngày phụ lục hợp đồng", required=True,
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
    bsd_ngay_ky_pl = fields.Datetime(string="Ngày ký phụ lục", help="Ngày ký phụ lục đồng sở hữu", readonly=True)
    state = fields.Selection([('nhap', 'Nháp'), ('xac_nhan', 'Xác nhận'),
                              ('dk_pl', 'Đã ký phụ lục'), ('huy', 'Hủy')],
                             string="Trạng thái", help="Trạng thái", required=True, default="nhap", tracking=1)
    bsd_loai_pl = fields.Selection([('dien_tich', 'Diện tích'), ('ten_ch', 'Tên Sản phẩm')], required=True,
                                   string="Loại phụ lục", help="Loại phụ lục hợp đồng", default="dien_tich",
                                   readonly=True,
                                   states={'nhap': [('readonly', False)]})
    bsd_dt_tt_id = fields.Many2one('bsd.dt_tt', string="Thay đổi diện tích",
                                   help="Phiếu cập nhật diện tích thông thủy thực tế",
                                   readonly=True,
                                   states={'nhap': [('readonly', False)]})
    bsd_ten_unit_moi = fields.Char(string="Tên Sản phẩm (mới)", help="Tên Sản phẩm mới",
                                   readonly=True,
                                   states={'nhap': [('readonly', False)]})
    bsd_ten_unit_cu = fields.Char(string="Tên Sản phẩm (cũ)", help="Tên Sản phẩm (cũ) trước khi được thay đổi",
                                  related='bsd_unit_id.bsd_ten_unit')

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

