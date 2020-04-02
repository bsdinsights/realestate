# -*- coding:utf-8 -*-

from odoo import models, fields, api


class ResCountry(models.Model):
    _inherit = 'res.country'

    state = fields.Selection([('active', "Đang sử dụng"),
                              ('inactive', "Không sử dụng")], string='Trạng thái',
                             default='active', tracking=1, help="Trạng thái")


class ResCountryState(models.Model):
    _inherit = 'res.country.state'

    state = fields.Selection([('active', "Đang sử dụng"),
                              ('inactive', "Không sử dụng")], string='Trạng thái',
                             default='active', tracking=1, help="Trạng thái")