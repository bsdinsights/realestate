# -*- coding:utf-8 -*-

from odoo import models, fields, api


class ResCountry(models.Model):
    _inherit = 'res.country'
    _order = 'sequence ASC'

    sequence = fields.Integer(string="Thứ tự")
    state = fields.Selection([('active', "Đang sử dụng"),
                              ('inactive', "Không sử dụng")], string='Trạng thái',
                             default='active', tracking=1, help="Trạng thái")


class ResCountryState(models.Model):
    _inherit = 'res.country.state'
    _order = 'sequence ASC'

    sequence = fields.Integer(string="Thứ tự")
    state = fields.Selection([('active', "Đang sử dụng"),
                              ('inactive', "Không sử dụng")], string='Trạng thái',
                             default='active', tracking=1, help="Trạng thái")


class ResPartnerBank(models.Model):
    _inherit = 'res.partner.bank'

    state = fields.Selection([('active', "Đang sử dụng"),
                              ('inactive', "Không sử dụng")], string='Trạng thái',
                             default='active', tracking=1, help="Trạng thái")