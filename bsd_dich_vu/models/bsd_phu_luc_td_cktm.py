# -*- coding:utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError
import datetime, calendar
import logging
_logger = logging.getLogger(__name__)


class BsdPLPTTT(models.Model):
    _name = 'bsd.pl_pttt'
    _description = "Phụ lục thay đổi phương thức thanh toán"
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _rec_name = 'bsd_ma'

    bsd_ma = fields.Char(string="Mã", help="Mã phụ lục hợp đồng thay đổi phương thức thanh toán",
                         required=True, readonly=True,
                         copy=False, default='/')
    _sql_constraints = [
        ('bsd_ma_unique', 'unique (bsd_ma)',
         'Mã phụ lục hợp đồng đã tồn tại !'),
    ]
    bsd_ngay = fields.Datetime(string="Ngày", help="Ngày tạo phụ lục hợp đồng thay đổi phương thức thanh toán",
                               required=True,
                               default=lambda self: fields.Datetime.now(),
                               readonly=True,
                               states={'nhap': [('readonly', False)]})
    bsd_khach_hang_id = fields.Many2one('res.partner', string="Khách hàng", help="Tên khách hàng", required=True,
                                        readonly=True,
                                        states={'nhap': [('readonly', False)]})
    bsd_hd_ban_id = fields.Many2one('bsd.hd_ban', string="Hợp đồng", help="Hợp đồng mua bán", required=True,
                                    readonly=True,
                                    states={'nhap': [('readonly', False)]})
    bsd_cs_tt_ht_id = fields.Many2one('bsd.cs_tt', string="PTTT hiện tại", readonly=True, required=True)
    bsd_ltt_ht_ids = fields.Many2many('bsd.lich_thanh_toan', relation='lich_ht_rel', string="Lịch thanh toán ht", readonly=True)

    @api.onchange('bsd_hd_ban_id')
    def _onchange_hd(self):
        self.bsd_du_an_id = self.bsd_hd_ban_id.bsd_du_an_id
        self.bsd_unit_id = self.bsd_hd_ban_id.bsd_unit_id
        self.bsd_cs_tt_ht_id = self.bsd_hd_ban_id.bsd_cs_tt_id
        self.update({'bsd_ltt_ht_ids': [(5,), (6, 0, self.bsd_hd_ban_id.bsd_ltt_ids.ids)]})

    bsd_du_an_id = fields.Many2one('bsd.du_an', string="Dự án",
                                   help="Tên dự án", required=True, readonly=True)
    bsd_unit_id = fields.Many2one('product.product',
                                  string="Sản phẩm", help="Tên Sản phẩm",
                                  required=True, readonly=True)
    bsd_dien_giai = fields.Char(string="Diễn giải", help="Diễn giải",
                                readonly=True,
                                states={'nhap': [('readonly', False)]})
    bsd_ngay_ky_pl = fields.Datetime(string="Ngày ký PL", help="Ngày ký phụ lục thay đổi PTTT", readonly=True)
    bsd_nguoi_xn_id = fields.Many2one('res.users', string="Người xác nhận", readonly=True)
    bsd_ngay_xn = fields.Date(string="Ngày xác nhận", help="Ngày xác nhận phụ lục hợp đồng", readonly=True)
    state = fields.Selection([('nhap', 'Nháp'), ('xac_nhan', 'Xác nhận'),
                              ('dk_pl', 'Đã ký phụ lục'), ('huy', 'Hủy')],
                             string="Trạng thái", help="Trạng thái", required=True, default="nhap", tracking=1)
    bsd_cs_tt_id = fields.Many2one('bsd.cs_tt', string="PTTT mới", help="Phương thức thanh toán mới",
                                   required=True)

    bsd_ltt_ids = fields.Many2many('bsd.lich_thanh_toan', relation='lich_moi_rel', string="Lịch thanh toán",
                                   readonly=True)
    bsd_ly_do = fields.Char(string="Lý do", readonly=True, tracking=2)

    def action_tao_pl(self):
        return {
            'type': 'ir.actions.act_window',
            'name': 'Phụ lục thay đổi PTTT',
            'res_model': 'bsd.pl_pttt',
            'res_id': self.id,
            'target': 'current',
            'view_mode': 'form'
        }

    # Xác nhận phụ lục hợp đồng
    def action_xac_nhan(self):
        if not self.bsd_ltt_ids:
            raise UserError(_("Chưa tạo lịch thanh toán mới.\nVui lòng kiểm tra lại thông tin."))
        self.write({
            'state': 'xac_nhan',
            'bsd_nguoi_xn_id': self.env.uid,
            'bsd_ngay_xn': fields.Date.today(),
        })

    # Ký phụ lục hợp đồng
    def action_ky_pl(self):
        if self.state == 'xac_nhan':
            action = self.env.ref('bsd_dich_vu.bsd_wizard_ky_pl_pttt_action').read()[0]
            return action

    # Hủy phụ lục hợp đồng
    def action_huy(self):
        if self.state != 'dk_pl':
            self.write({
                'state': 'huy'
            })

    # Không duyệt phụ lục hợp đồng
    def action_khong_duyet(self):
        if self.state == 'xac_nhan':
            action = self.env.ref('bsd_dich_vu.bsd_wizard_khong_duyet_pl_pttt_action').read()[0]
            return action

    @api.model
    def create(self, vals):
        sequence = self.env['ir.sequence']
        if 'bsd_du_an_id' in vals:
            du_an = self.env['bsd.du_an'].browse(vals['bsd_du_an_id'])
            sequence = du_an.get_ma_bo_cn(loai_cn=self._name)
        if not sequence:
            raise UserError(_('Dự án chưa có quy định mã phụ lục thay đổi phương thức thanh toán.\n'
                              'Vui lòng kiểm tra lại thanh tin.'))
        vals['bsd_ma'] = sequence.next_by_id()
        res = super(BsdPLPTTT, self).create(vals)
        return res
