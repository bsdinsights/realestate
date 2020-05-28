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
        WITH price AS (WITH max_pricelist AS (SELECT item.id,item.product_tmpl_id,item.fixed_price 
            from product_pricelist_item AS item
                LEFT JOIN product_pricelist AS pricelist ON pricelist.id = item.pricelist_id 
                JOIN (SELECT 
                item.product_tmpl_id AS unit,
                max(pricelist.create_date) AS max_date
            FROM product_pricelist_item AS item
                LEFT JOIN product_pricelist AS pricelist ON pricelist.id = item.pricelist_id
            GROUP BY item.product_tmpl_id) AS max_item ON max_item.unit = item.product_tmpl_id 
            AND pricelist.create_date = max_item.max_date)
        SELECT 
            unit.id AS unit_id,
            CASE
                WHEN dot_mb.id IS NOT NULL AND item.fixed_price IS NOT NULL THEN item.fixed_price
                WHEN max_item.id IS NOT NULL AND max_item.fixed_price IS NOT NULL THEN max_item.fixed_price          
                ELSE unit.bsd_tong_gb
                END 
                AS chot_gia
                FROM product_template AS unit
                    LEFT JOIN bsd_dot_mb AS dot_mb ON dot_mb.id = unit.bsd_dot_mb_id
                    LEFT JOIN product_pricelist AS pricelist ON pricelist.id = dot_mb.bsd_bang_gia_id
                    LEFT JOIN product_pricelist_item AS item ON item.pricelist_id = pricelist.id and item.product_tmpl_id = unit.id
                    LEFT JOIN max_pricelist AS max_item ON max_item.product_tmpl_id = unit.id)
                SELECT 
                    toa.id AS id_toa,
                    toa.bsd_ten_tn,
                    tang.id AS id_tang,
                    tang.bsd_ma_tang,
                    unit.id AS id_unit,
                    unit.name,
                    unit.state, 
                    giu_cho.so_giu_cho_unit,
                    price.chot_gia AS gia_ban
                FROM bsd_toa_nha AS toa
                LEFT JOIN bsd_tang AS tang 
                    ON toa.id = tang.bsd_toa_nha_id
                LEFT JOIN product_template AS unit 
                    ON tang.id = unit.bsd_tang_id
                LEFT JOIN (SELECT unit.product_tmpl_id,COUNT(*) AS so_giu_cho_unit 
                                            FROM bsd_giu_cho AS giu_cho
                                            LEFT JOIN product_product AS unit ON unit.id = giu_cho.bsd_unit_id
                                            GROUP BY unit.product_tmpl_id) AS giu_cho ON giu_cho.product_tmpl_id = unit.id
                LEFT JOIN price ON price.unit_id = unit.id
                WHERE 
                    (toa.bsd_du_an_id = %s)
                ORDER BY
                    toa.id, tang.bsd_stt, unit.bsd_stt
            """,
            (data['bsd_du_an_id'],))
        item_ids = [x for x in self.env.cr.fetchall()]
        return item_ids


