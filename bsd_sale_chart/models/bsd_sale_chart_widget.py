# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from odoo.exceptions import UserError
import logging
_logger = logging.getLogger(__name__)


class BsdSaleChartWidget(models.AbstractModel):
    _name = 'bsd.sale_chart.widget'
    _description = 'Sale chart widget'

    bsd_du_an_id = fields.Many2one('bsd.du_an', string="Dự án")
    bsd_dot_mb_id = fields.Many2one('bsd.dot_mb', string="Đợt mở bán")

    @api.model
    def action_search(self, data):
        if not data['bsd_du_an_id']:
            raise UserError("Vui lòng điền trường dự án")
        self.env.cr.execute(
            """
                SELECT 
                    toa.id,toa.bsd_ma_ht,
                    tang.id,tang.bsd_ma_tang,
                    unit.id,unit.name,unit.state  
                FROM 
                    bsd_toa_nha AS toa
                LEFT JOIN 
                    bsd_tang AS tang ON toa.id = tang.bsd_toa_nha_id
                LEFT JOIN 
                    product_template AS unit ON tang.id = unit.bsd_tang_id
                WHERE 
                    (toa.bsd_du_an_id = %s)
                ORDER BY
                    toa.id, tang.id, unit.id
            """,
            (data['bsd_du_an_id'],))
        item_ids = [x for x in self.env.cr.fetchall()]
        return item_ids


