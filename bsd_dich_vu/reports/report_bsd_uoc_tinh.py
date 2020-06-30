# -*- coding:utf-8 -*-

from odoo import api, models, fields
import logging
import datetime
from num2words import num2words
_logger = logging.getLogger(__name__)


class ReportBsdUocTinhCKTT(models.AbstractModel):
    _name = 'report.bsd_dich_vu.bsd_uoc_tinh_view'

    @api.model
    def _get_report_values(self, docids, data=None):
        res = {}
        # lấy recordset hợp đồng
        hd_ban = self.env['bsd.hd_ban'].browse(data['ids'])
        # lấy thông tin khách khách hàng
        khach_hang = hd_ban.bsd_khach_hang_id
        # lấy đợt mở bán
        dot_mb = hd_ban.bsd_dot_mb_id
        if dot_mb.bsd_ck_ttth_id:
            ttth = dot_mb.bsd_ck_ttth_id.bsd_ct_ids.\
                filtered(lambda c: c.bsd_tu_ngay < data['bsd_ngay_ut'] < c.bsd_den_ngay)
        if dot_mb.bsd_ck_ttn_id:
            ck_ttn = dot_mb.bsd_ck_ttn_id.bsd_ct_ids.\
                filtered(lambda c: c.bsd_tu_ngay < data['bsd_ngay_ut'] < c.bsd_den_ngay)
        res['khach_hang'] = {
            'name': khach_hang.name,
            'cmnd': khach_hang.bsd_cmnd,
            'phone': khach_hang.phone,
            'email': khach_hang.email,
            'dia_chi': khach_hang.bsd_dia_chi_lh,
            'so_can_ho': hd_ban.bsd_unit_id.bsd_ten_unit,
            'hop_dong': hd_ban.bsd_unit_id.bsd_ma_unit + " - " + hd_ban.bsd_ma_hd_ban,
        }
        res['ck_ttth'] = {

        }
        res['doc_ids'] = data['ids']
        res['doc_model'] = data['model']
        res['bsd_ngay_ut'] = data['bsd_ngay_ut']
        res['bsd_tien_ut'] = data['bsd_tien_ut']
        return res