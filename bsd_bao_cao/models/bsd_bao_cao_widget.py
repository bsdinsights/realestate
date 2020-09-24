# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from odoo.exceptions import UserError
import itertools
import logging
_logger = logging.getLogger(__name__)


class BsdBaoCaoWidget(models.AbstractModel):
    _name = 'bsd.bao_cao.widget'
    _description = 'Báo cáo'

    bsd_du_an_id = fields.Many2one('bsd.du_an', string="Dự án", help="Dự án")
    bsd_tu_ngay = fields.Date(string="Từ ngày")
    bsd_den_ngay = fields.Date(string="Đến ngày")

    @api.model
    def action_export_xlsx(self, data):
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
            rp_dtt = self._bao_cao_dot_tt(where=where)
            _logger.debug(rp_dtt)

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
                SELECT 
                        hd.id,
                        du_an.bsd_ten_da, 
                        toa.bsd_ten_tn,
                        sp.bsd_ten_unit, 
                        sp.state, 
                        hd.bsd_ma_hd_ban,
                        cs.bsd_ma_cstt,
                        lich_tt.bsd_ten_dtt,
                        lich_tt.bsd_tien_dot_tt,
                        chi_tiet.bsd_tl_tt,
                        lich_tt.bsd_ngay_hh_tt
                        FROM bsd_du_an AS du_an
                    JOIN bsd_toa_nha AS toa ON toa.bsd_du_an_id = du_an.id
                    JOIN product_template AS sp ON sp.bsd_toa_nha_id = toa.id
                    JOIN product_product AS unit ON unit.product_tmpl_id = sp.id
                    JOIN bsd_hd_ban AS hd ON hd.bsd_unit_id = unit.id
                    LEFT JOIN bsd_cs_tt AS cs ON hd.bsd_cs_tt_id = cs.id
                    LEFT JOIN bsd_lich_thanh_toan AS lich_tt ON lich_tt.bsd_hd_ban_id = hd.id
                    LEFT JOIN bsd_cs_tt_ct AS chi_tiet ON lich_tt.bsd_cs_tt_ct_id = chi_tiet.id        
                """ + where + "AND lich_tt.bsd_loai = 'dtt' " + "ORDER BY toa.id, sp.bsd_stt, lich_tt.bsd_stt")
        raw_data = [x for x in self.env.cr.fetchall()]
        _logger.debug("dữ liệu group")
        data = []
        for key, group in itertools.groupby(raw_data, key=lambda x: x[0]):
            lich_tt = []
            list_group = list(group)
            for items in list_group:
                lich_tt.append(items[7:])
            key_and_group = list(list_group[0])[1:7] + [lich_tt]
            if key_and_group[3] == 'chuan_bi':
                key_and_group[3] = 'Chuẩn bị'
            elif key_and_group[3] == 'san_sang':
                key_and_group[3] = 'Sẵn sàng'
            elif key_and_group[3] == 'dat_cho':
                key_and_group[3] = 'Đặt chỗ'
            elif key_and_group[3] == 'giu_cho':
                key_and_group[3] = 'Giữ chỗ'
            elif key_and_group[3] == 'dat_coc':
                key_and_group[3] = 'Đặt cọc'
            elif key_and_group[3] == 'chuyen_coc':
                key_and_group[3] = 'Chuyển cọc'
            elif key_and_group[3] == 'da_tc':
                key_and_group[3] = 'Đã thu cọc'
            elif key_and_group[3] == 'ht_dc':
                key_and_group[3] = 'Hoàn tất đặt cọc'
            elif key_and_group[3] == 'tt_dot_1':
                key_and_group[3] = 'Thanh toán đợt 1'
            elif key_and_group[3] == 'ky_tt_coc':
                key_and_group[3] = 'Ký thỏa thuận cọc'
            elif key_and_group[3] == 'du_dk':
                key_and_group[3] = 'Đủ điều kiện'
            elif key_and_group[3] == 'da_ban':
                key_and_group[3] = 'Đã bán'
            
            data.append(key_and_group)
        return data
