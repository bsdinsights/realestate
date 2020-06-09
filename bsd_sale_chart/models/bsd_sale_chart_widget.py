# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from odoo.exceptions import UserError
import logging
_logger = logging.getLogger(__name__)


class BsdSaleChartWidget(models.AbstractModel):
    _name = 'bsd.sale_chart.widget'
    _description = 'Sale chart widget'

    bsd_du_an_id = fields.Many2one('bsd.du_an', string="Dự án", help="Dự án")
    bsd_dot_mb_id = fields.Many2one('bsd.dot_mb', string="Đợt mở bán", help="Đợt mở bán")
    bsd_unit = fields.Char(string='Mã căn hộ', help="Mã căn hộ")
    bsd_tu_gia = fields.Float(string="Giá từ", help="Giá từ")
    bsd_den_gia = fields.Float(string="Giá đến", help="Giá đến")
    bsd_tu_dt = fields.Float(string="Từ diện tích")
    bsd_den_dt = fields.Float(string="Đến diện tích")
    bsd_view = fields.Selection([('1', 'Phố'),
                                 ('2', 'Hồ bơi'),
                                 ('3', 'Công viên'),
                                 ('4', 'Mặt tiền'),
                                 ('5', 'Bãi biển/sông/hồ/núi'),
                                 ('6', 'Rừng'),
                                 ('7', 'Cao tốc'),
                                 ('8', 'Hồ'),
                                 ('9', 'Biển')], string="View", help="Góc nhìn của căn hộ")
    bsd_huong = fields.Selection([('1', 'Đông'),
                                  ('2', 'Tây'),
                                  ('3', 'Nam'),
                                  ('4', 'Bắc'),
                                  ('5', 'Đông nam'),
                                  ('6', 'Đông bắc'),
                                  ('7', 'Tây nam'),
                                  ('8', 'Tây bắc')], string="Hướng", help="Hướng nhà")

    @api.model
    def action_search(self, data):
        if not data['bsd_du_an_id']:
            raise UserError("Vui lòng điền trường dự án")
        where = ' WHERE (toa.bsd_du_an_id = {0}) '.format(data['bsd_du_an_id'])
        if data['bsd_dot_mb_id']:
            where += 'AND (unit.bsd_dot_mb_id = {0}) '.format(data['bsd_dot_mb_id'])
        if data['bsd_unit']:
            where += "AND (unit.bsd_ten_unit LIKE '{0}%') ".format(data['bsd_unit'])
        if data['bsd_view']:
            where += "AND (unit.bsd_view = '{0}') ".format(data['bsd_view'])
        if data['bsd_huong']:
            where += "AND (unit.bsd_huong = '{0}') ".format(data['bsd_huong'])
        if data['bsd_tu_gia']:
            where += 'AND (price.chot_gia >= {0}) '.format(data['bsd_tu_gia'])
        if data['bsd_den_gia']:
            where += 'AND (price.chot_gia <= {0}) '.format(data['bsd_den_gia'])
        if data['bsd_tu_dt']:
            where += 'AND (unit.bsd_dt_sd >= {0}) '.format(data['bsd_tu_dt'])
        if data['bsd_den_dt']:
            where += 'AND (unit.bsd_dt_sd <= {0}) '.format(data['bsd_den_dt'])
        _logger.debug(where)
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
                    price.chot_gia AS gia_ban,
                    unit.bsd_dt_sd AS dien_tich,
                    loai.bsd_ten_nhom AS loai,
                    unit_product.id AS product
                FROM bsd_toa_nha AS toa
                LEFT JOIN bsd_tang AS tang 
                    ON toa.id = tang.bsd_toa_nha_id
                LEFT JOIN product_template AS unit 
                    ON tang.id = unit.bsd_tang_id
                LEFT JOIN (SELECT unit.product_tmpl_id,COUNT(*) AS so_giu_cho_unit 
                                            FROM bsd_giu_cho AS giu_cho
                                            LEFT JOIN product_product AS unit 
                                                ON unit.id = giu_cho.bsd_unit_id AND giu_cho.state IN ('dat_cho','giu_cho')
                                            GROUP BY unit.product_tmpl_id) AS giu_cho ON giu_cho.product_tmpl_id = unit.id
                LEFT JOIN price ON price.unit_id = unit.id
                LEFT JOIN bsd_loai_sp AS loai
                    ON loai.id = unit.bsd_loai_sp_id
                LEFT JOIN product_product AS unit_product ON unit_product.product_tmpl_id = unit.id
                """ + where + "ORDER BY toa.id, tang.bsd_stt, unit.bsd_stt")

        item_ids = [x for x in self.env.cr.fetchall()]
        return item_ids


