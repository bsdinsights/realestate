# -*- coding:utf-8 -*-

from odoo import models, fields, api
from odoo.exceptions import UserError
from odoo.tools import float_utils
import logging
_logger = logging.getLogger(__name__)


class BsdLaiPhat(models.Model):
    _name = 'bsd.lai_phat'
    _description = 'Lãi phạt'
    _rec_name = 'bsd_hd_ban_id'

    bsd_ngay_lp = fields.Datetime(string="Ngày tính phạt", readonly=True, required=True)
    bsd_hd_ban_id = fields.Many2one('bsd.hd_ban', string="Hợp đồng", readonly=True, required=True)
    bsd_dot_tt_id = fields.Many2one('bsd.lich_thanh_toan', string="Đợt thanh toán", required=True, readonly=True)
    bsd_phieu_thu_id = fields.Many2one('bsd.phieu_thu', string="Phiếu TT", required=True, readonly=True)
    bsd_tien_tt = fields.Monetary(string="Tiền thanh toán", readonly=True)
    bsd_tien_phat = fields.Monetary(string="Tiền phạt", readonly=True)
    bsd_so_ngay = fields.Integer(string="Số ngày", readonly=True)
    company_id = fields.Many2one('res.company', string='Công ty', default=lambda self: self.env.company)
    currency_id = fields.Many2one(related="company_id.currency_id", string="Tiền tệ", readonly=True)

    bsd_tien_da_tt = fields.Monetary(string="Đã thanh toán", help="Đã thanh toán",
                                     compute="_compute_tien_tt", store=True)
    bsd_tien_phai_tt = fields.Monetary(string="Phải thanh toán", help="Đã thanh toán",
                                       compute="_compute_tien_tt", store=True)
    bsd_thanh_toan = fields.Selection([('chua_tt', 'Chưa thanh toán'),
                                       ('dang_tt', 'Đang thanh toán'),
                                       ('da_tt', 'Đã thanh toán')], string="Thanh toán",
                                      help="Thanh toán", compute='_compute_tien_tt', store=True)
    bsd_ct_ids = fields.One2many('bsd.cong_no_ct', 'bsd_lai_phat_id',
                                 domain=[('bsd_loai', '=', 'pt_lp'), ('state', '=', 'hieu_luc')],
                                 string="Chi tiết")

    @api.depends('bsd_ct_ids', 'bsd_ct_ids.bsd_tien_pb', 'bsd_tien_phat')
    def _compute_tien_tt(self):
        for each in self:
            each.bsd_tien_da_tt = sum(each.bsd_ct_ids.mapped('bsd_tien_pb'))
            each.bsd_tien_phai_tt = each.bsd_tien_phat - each.bsd_tien_da_tt

            if each.bsd_tien_phai_tt == 0:
                each.bsd_thanh_toan = 'da_tt'
            elif 0 < each.bsd_tien_phai_tt < each.bsd_tien_phat:
                each.bsd_thanh_toan = 'dang_tt'
            else:
                each.bsd_thanh_toan = 'chua_tt'

    def _get_name(self):
        lp = self
        name = "%s - %s" % (lp.bsd_hd_ban_id.bsd_ma_hd_ban,
                            lp.bsd_dot_tt_id.bsd_ten_dtt)
        return name

    def name_get(self):
        res = []
        for lp in self:
            name = lp._get_name()
            res.append((lp.id, name))
        return res
