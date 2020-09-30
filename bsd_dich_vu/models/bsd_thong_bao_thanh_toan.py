# -*- coding:utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError
import logging

_logger = logging.getLogger(__name__)


class BsdThongBaoThanhToan(models.Model):
    _name = 'bsd.tb_tt_nn'
    _description = "Thông báo thanh toán, nhắc nợ"
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _rec_name = 'bsd_ma_tb'

    bsd_ma_tb = fields.Char(string="Mã", help="Mã thông báo thanh toán, nhắc nợ", required=True, readonly=True,
                            copy=False, default='/')
    _sql_constraints = [
        ('bsd_ma_tb_unique', 'unique (bsd_ma_tb)',
         'Mã thông báo thanh toán đã tồn tại !')
    ]
    bsd_ngay_tao_tb = fields.Datetime(string="Ngày", help="Ngày tạo thông báo thanh toán",
                                      required=True, default=lambda self: fields.Datetime.now(),
                                      readonly=True,
                                      states={'nhap': [('readonly', False)]})
    bsd_tieu_de = fields.Char(string="Tiêu đề", help="Tiêu đề thông báo", required=True,
                              readonly=True,
                              states={'nhap': [('readonly', False)]})

    bsd_ngay_in = fields.Datetime(string="Ngày in", help="Ngày in thông báo bàn giao", readonly=True)
    bsd_nguoi_xn_id = fields.Many2one('res.users', string="Người xác nhận",
                                      help="Người xác nhận thông tin trên thông báo thanh toán nhắc nợ", readonly=True)
    bsd_ngay_xn = fields.Datetime(string="Ngày xác nhận", help="Ngày xác nhận thông tin thông báo nhắc nợ",
                                  readonly=True)
    bsd_ngay_gui = fields.Datetime(string="Ngày gửi", help="Ngày gửi", readonly=True)
    bsd_loai = fields.Selection([('tb_tt', 'Thông báo thanh toán'),
                                 ('tb_tt_dot_cuoi', 'Thông báo thanh toán đợt cuối'),
                                 ('tb_nn', 'Thông báo nhắc nợ')], string="Loại", required=True, help="Phân loại thông báo")
    bsd_du_an_id = fields.Many2one('bsd.du_an', string="Dự án", help="Dự án", required=True,
                                   readonly=True,
                                   states={'nhap': [('readonly', False)]})
    bsd_unit_id = fields.Many2one('product.product', string="Sản phẩm", help="Sản phẩm", required=True,
                                  readonly=True,
                                  states={'nhap': [('readonly', False)]})
    bsd_hd_ban_id = fields.Many2one('bsd.hd_ban', string="Hợp đồng", help="Hợp đồng", required=True,
                                    readonly=True,
                                    states={'nhap': [('readonly', False)]})
    bsd_dot_tt_id = fields.Many2one('bsd.lich_thanh_toan', string="Đợt thanh toán",
                                    help="Đợt thanh toán đến hạn", required=True,
                                    readonly=True,
                                    states={'nhap': [('readonly', False)]})

    bsd_khach_hang_id = fields.Many2one('res.partner', string="Khách hàng", help="Khách hàng", required=True,
                                        readonly=True,
                                        states={'nhap': [('readonly', False)]})
    bsd_dien_giai = fields.Char(string="Diễn giải", help="Diễn giải",
                                readonly=True,
                                states={'nhap': [('readonly', False)]})
    company_id = fields.Many2one('res.company', string='Công ty', default=lambda self: self.env.company)
    currency_id = fields.Many2one(related="company_id.currency_id", string="Tiền tệ", readonly=True)
    state = fields.Selection([('nhap', 'Nháp'),
                              ('xac_nhan', 'Xác nhận'),
                              ('da_gui', 'Đã gửi'),
                              ('huy', 'Hủy')],
                             string="Trạng thái", default="nhap", required=True, readonly=True, tracking=1)

    @api.onchange('bsd_hd_ban_id')
    def _onchange_hd_ban(self):
        self.bsd_du_an_id = self.bsd_hd_ban_id.bsd_du_an_id
        self.bsd_unit_id = self.bsd_hd_ban_id.bsd_unit_id

    def action_xac_nhan(self):
        if self.state == 'nhap':
            self.write({
                'state': 'xac_nhan',
                'bsd_nguoi_xn_id': self.env.uid,
                'bsd_ngay_xn': fields.Datetime.now()
            })

    def action_in_tb(self):
        return self.env.ref('bsd_dich_vu.bsd_tb_tt_nn_report_action').read()[0]

    # DV.16.05 Hủy thông báo bàn giao
    def action_huy(self):
        if self.state == 'nhap':
            self.write({
                'state': 'huy'
            })

    @api.model
    def create(self, vals):
        sequence = False
        if 'bsd_du_an_id' in vals:
            du_an = self.env['bsd.du_an'].browse(vals['bsd_du_an_id'])
            sequence = du_an.get_ma_bo_cn(loai_cn=self._name)
            _logger.debug(du_an)
        if not sequence:
            raise UserError(_('Dự án chưa có mã thông báo thanh toán/ nhắc nợ'))
        vals['bsd_ma_tb'] = sequence.next_by_id()
        return super(BsdThongBaoThanhToan, self).create(vals)
