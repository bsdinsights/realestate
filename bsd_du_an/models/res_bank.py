# -*- coding:utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError, UserError
from datetime import datetime
import logging

_logger = logging.getLogger(__name__)


class ResPartnerBank(models.Model):
    _inherit = 'res.partner.bank'

    bsd_du_an_id = fields.Many2one('bsd.du_an', string="Dự án", help="Dự án")
    bsd_tu_ngay = fields.Date(string="Từ ngày", help="Ngày bắt đầu áp dụng tài khoản ngân hàng")
    bsd_den_ngay = fields.Date(string="Đến ngày", help="Ngày kết thúc áp dụng tài khoản ngân hàng")
    bsd_tk_chinh = fields.Boolean(string="Tài khoản chính", help="Tài khoản sử dụng mặc định")