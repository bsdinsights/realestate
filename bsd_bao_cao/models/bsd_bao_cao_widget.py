# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from odoo.exceptions import UserError
import logging
_logger = logging.getLogger(__name__)


class BsdBaoCaoWidget(models.AbstractModel):
    _name = 'bsd.bao_cao.widget'
    _description = 'Báo cáo'

    bsd_du_an_id = fields.Many2one('bsd.du_an', string="Dự án", help="Dự án")
    bsd_tu_ngay = fields.Date(string="Từ ngày")
    bsd_den_ngay = fields.Date(string="Đến ngày")

    @api.model
    def action_search(self, data):
        if not data['bsd_du_an_id']:
            raise UserError("Vui lòng điền trường dự án")
        where = ' WHERE (du_an.id = {0}) '.format(data['bsd_du_an_id'])
        if data['bsd_tu_ngay']:
            where += 'AND (hd.bsd_ngay_hd_ban >= {0}) '.format(data['bsd_tu_ngay'])
        if data['bsd_den_ngay']:
            where += 'AND (hd.bsd_ngay_hd_ban <= {0}) '.format(data['bsd_den_ngay'])
        if not data['bsd_loai']:
            raise UserError("Vui lòng chọn loại báo cáo")
        elif data['bsd_loai'] == 'dot_tt':
            return self._bao_cao_dot_tt(where=where)

    @api.model
    def _bao_cao_dot_tt(self, where):
        self.env.cr.execute("""
                SELECT du_an.bsd_ten_da, 
                        toa.bsd_ten_tn,
                        sp.bsd_ten_unit, 
                        sp.state, 
                        hd.bsd_ma_hd_ban,
                        cs.bsd_ma_cstt,
                        lich_tt.bsd_ten_dtt,
                        lich_tt.bsd_tien_dot_tt,
                        lich_tt.bsd_ngay_hh_tt,
                        chi_tiet.bsd_tl_tt
                        FROM bsd_du_an AS du_an
                    JOIN bsd_toa_nha AS toa ON toa.bsd_du_an_id = du_an.id
                    JOIN product_template AS sp ON sp.bsd_toa_nha_id = toa.id
                    JOIN product_product AS unit ON unit.product_tmpl_id = sp.id
                    JOIN bsd_hd_ban AS hd ON hd.bsd_unit_id = unit.id
                    LEFT JOIN bsd_cs_tt AS cs ON hd.bsd_cs_tt_id = cs.id
                    LEFT JOIN bsd_lich_thanh_toan AS lich_tt ON lich_tt.bsd_hd_ban_id = hd.id
                    LEFT JOIN bsd_cs_tt_ct AS chi_tiet ON lich_tt.bsd_cs_tt_ct_id = chi_tiet.id        
                """ + where + "ORDER BY toa.id, sp.bsd_stt")
        return [x for x in self.env.cr.fetchall()]
