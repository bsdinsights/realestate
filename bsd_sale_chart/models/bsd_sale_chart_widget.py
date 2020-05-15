# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
import logging
_logger = logging.getLogger(__name__)


class BsdSaleChartWidget(models.AbstractModel):
    _name = 'bsd.sale_chart.widget'
    _description = 'Sale chart widget'

    bsd_du_an_id = fields.Many2one('bsd.du_an', string="Dự án")
    bsd_dot_mb_id = fields.Many2one('bsd.dot_mb', string="Đợt mở bán")

    @api.model
    def call_back(self):
        _logger.debug("goi toi day")


