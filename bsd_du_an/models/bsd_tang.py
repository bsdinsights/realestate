# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError
import logging
_logger = logging.getLogger(__name__)


class BsdFloor(models.Model):
    _name = "bsd.tang"
    _rec_name = 'bsd_ma_tang'
    _description = 'Thông tin tầng'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    bsd_ten_tang = fields.Char(string="Tên tầng", required=True, help="Tên tầng")
    bsd_ma_tang = fields.Char(string="Mã tầng", help="Mã tầng", compute='_compute_ma_tang', store=True)
    _sql_constraints = [
        ('bsd_ma_tang_unique', 'unique (bsd_ma_tang)',
         'Mã tầng đã tồn tại !'),
    ]

    @api.depends('bsd_toa_nha_id.bsd_ma_ht', 'bsd_ten_tang')
    def _compute_ma_tang(self):
        for each in self:
            if each.bsd_toa_nha_id and each.bsd_ten_tang:
                du_an = each.bsd_toa_nha_id.bsd_du_an_id
                toa_nha = each.bsd_toa_nha_id
                each.bsd_ma_tang = du_an.bsd_ma_da + du_an.bsd_dd_da + toa_nha.bsd_ma_tn + du_an.bsd_dd_khu + each.bsd_ten_tang
                _logger.debug(each.bsd_ma_tang)
    bsd_stt = fields.Integer(string="Số thứ tự", help="Số thứ tự sắp xếp của tầng", required=True)
    bsd_dien_giai = fields.Char(string="Diễn giải",
                                help="Thông tin chi tiết về tòa nhà")
    bsd_du_an_id = fields.Many2one('bsd.du_an', string="Dự án", required=True, help="Tên dư án",
                                   readonly=True,
                                   states={'chuan_bi': [('readonly', False)]})
    bsd_toa_nha_id = fields.Many2one('bsd.toa_nha', string="Tòa nhà", required=True, help="Tên tòa nhà",
                                     readonly=True,
                                     states={'chuan_bi': [('readonly', False)]})
    active = fields.Boolean(default=True)
    bsd_unit_ids = fields.One2many('product.template', 'bsd_tang_id', string="Danh sách sản phẩm")
    state = fields.Selection(related='bsd_du_an_id.state', store=True)

    def name_get(self):
        res = []
        for toa in self:
            res.append((toa.id, toa.bsd_ten_tang))
        return res

    @api.constrains('bsd_du_an_id')
    def _constrains_da(self):
        if self.bsd_du_an_id.state != 'chuan_bi':
            raise UserError(_("Dự án đã phát hành.\nVui lòng kiểm tra lại thông tin."))