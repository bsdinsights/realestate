# -*- coding:utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError
import datetime
import logging
_logger = logging.getLogger(__name__)


class BsdCapNhatHTT(models.Model):
    _name = 'bsd.cn_htt'
    _description = "Cập nhật hạn thanh toán của hợp đồng"
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _rec_name = 'bsd_ten'

    bsd_ma = fields.Char(string="Mã", help="Mã cập nhật ngày đến hạn thanh toán của hợp đồng", required=True, readonly=True,
                         copy=False, default='/')
    _sql_constraints = [
        ('bsd_ma_unique', 'unique (bsd_ma)',
         'Mã phiếu cập nhật ngày đến hạn thanh toán đã tồn tại !')
    ]
    bsd_ten = fields.Char(string="Tiêu đề", help="Tiêu đề", required=True,
                          readonly=True,
                          states={'nhap': [('readonly', False)]})
    bsd_ngay = fields.Date(string="Ngày tạo", required=True, default=lambda self: fields.Datetime.now(),
                               readonly=True,
                               states={'nhap': [('readonly', False)]})
    bsd_du_an_id = fields.Many2one('bsd.du_an', string="Dự án", help="Dự án", required=True,
                                   readonly=True,
                                   states={'nhap': [('readonly', False)]})
    bsd_hd_ban_id = fields.Many2one('bsd.hd_ban', string="Hợp đồng", help="Dự án", required=True, readonly=True,
                                    states={'nhap': [('readonly', False)]})
    bsd_unit_id = fields.Many2one('product.product', string="Sản phẩm", help="Sản phẩm",
                                  required=True, readonly=True, states={'nhap': [('readonly', False)]})
    bsd_ly_do = fields.Char(string="Lý do", readonly=True, tracking=2)
    bsd_ct_ids = fields.One2many('bsd.cn_htt_ct', 'bsd_cn_htt_id', string="Cập nhật HTT chi tiết", readonly=True)

    @api.onchange('bsd_hd_ban_id')
    def _onchange_hd_ban(self):
        self.bsd_unit_id = self.bsd_hd_ban_id.bsd_unit_id

    bsd_ngay_xn = fields.Datetime(string="Ngày xác nhận", readonly=True, help="Ngày xác nhận")
    bsd_nguoi_xn_id = fields.Many2one('res.users', string="Người xác nhận", readonly=True, help="Người xác nhận")
    bsd_ngay_duyet = fields.Datetime(string="Ngày duyệt", readonly=True, help="Ngày duyệt")
    bsd_nguoi_duyet_id = fields.Many2one('res.users', string="Người duyệt", help="Người duyệt", readonly=True)
    state = fields.Selection([('nhap', 'Nháp'), ('xac_nhan', 'Xác nhận'),
                              ('duyet', 'Duyệt'), ('huy', 'Hủy')],
                             string="Trạng thái", default="nhap", required=True, readonly=True, tracking=1)

    @api.model
    def create(self, vals):
        sequence = None
        if 'bsd_du_an_id' in vals:
            du_an = self.env['bsd.du_an'].browse(vals['bsd_du_an_id'])
            sequence = du_an.get_ma_bo_cn(loai_cn=self._name)
        if not sequence:
            raise UserError(_('Dự án chưa có mã cập nhật ngày đến hạn thanh toán.'))
        vals['bsd_ma'] = sequence.next_by_id()
        return super(BsdCapNhatHTT, self).create(vals)

    @api.model
    def _name_search(self, name='', args=None, operator='ilike', limit=100, name_get_uid=None):
        args = list(args or [])
        if name:
            if operator == 'ilike':
                args += [('bsd_ten', operator, name)]
            elif operator == '=':
                args += [('bsd_ma', operator, name)]
        access_rights_uid = name_get_uid or self._uid
        ids = self._search(args, limit=limit, access_rights_uid=access_rights_uid)
        recs = self.browse(ids)
        return models.lazy_name_get(recs.with_user(access_rights_uid))


class BsdCapNhatHTTChiTiet(models.Model):
    _name = 'bsd.cn_htt_ct'
    _description = "Chi tiết các đợt thanh toán gia hạn"
    _rec_name = 'bsd_dot_tt_id'

    bsd_cn_htt_id = fields.Many2one('bsd.cn_htt', ondelete='cascade',
                                    string="Cập nhật QSDĐ",
                                    help="Tên cập nhật hạn thanh toán hợp đồng", required=True,
                                    readonly=True,
                                    states={'nhap': [('readonly', False)]})
    bsd_hd_ban_id = fields.Many2one('bsd.hd_ban', string="Hợp đồng", readonly=True, required=True)
    bsd_dot_tt_id = fields.Many2one('bsd.lich_thanh_toan', string="Đợt TT", required=True, readonly=True,
                                    states={'nhap': [('readonly', False)]})
    bsd_stt = fields.Integer(related='bsd_dot_tt_id.bsd_stt')
    bsd_ngay_htt_ht = fields.Date(string="Hạn TT hiện tại", help="Hạn thanh toán hiện tại của đợt", readonly=True,
                                  states={'nhap': [('readonly', False)]})

    @api.onchange('bsd_dot_tt_id')
    def _onchange_dot(self):
        self.bsd_ngay_htt_ht = self.bsd_dot_tt_id.bsd_ngay_hh_tt

    bsd_ngay_htt_moi = fields.Date(string="Hạn TT mới", help="Hạn thanh toán mới của đợt", readonly=True,
                                   states={'nhap': [('readonly', False)]})
    state = fields.Selection([('nhap', 'Nháp'), ('xac_nhan', 'Xác nhận'),
                              ('duyet', 'Duyệt'), ('huy', 'Hủy')],
                             string="Trạng thái", default="nhap", required=True, readonly=True)

    def action_huy(self):
        if self.state == 'nhap':
            self.write({'state': 'huy'})

    # Tên hiện thị record
    def name_get(self):
        res = []
        for ct in self:
            ma_cn = ct.bsd_cn_htt_id.bsd_ma
            ten_dot = ct.bsd_dot_tt_id.bsd_ten_dtt
            res.append((ct.id, "{0} - {1}".format(ma_cn, ten_dot)))
        return res
