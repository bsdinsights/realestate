# -*- coding:utf-8 -*-

from odoo import api, models, fields
from odoo.exceptions import UserError
from odoo.tools.float_utils import float_round,float_repr
import logging
import datetime
_logger = logging.getLogger(__name__)


class ReportBsdUocTinhCKTT(models.AbstractModel):
    _name = 'report.bsd_dich_vu.bsd_uoc_tinh_view'

    @api.model
    def _get_report_values(self, docids, data=None,):
        doc = {}
        _logger.debug(data)
        # lấy recordset hợp đồng
        hd_ban = self.env['bsd.hd_ban'].browse(data['ids'])
        currency_id = hd_ban.currency_id
        # lấy thông tin khách khách hàng
        khach_hang = hd_ban.bsd_khach_hang_id
        # lấy đợt mở bán
        dot_mb = hd_ban.bsd_dot_mb_id
        ngay_ut = datetime.datetime.strptime(data['bsd_ngay_ut'], '%Y-%m-%d').date()
        ck_ttth = False
        ck_ttn = False
        if dot_mb.bsd_ck_ttth_id:
            item_ttth = dot_mb.bsd_ck_ttth_id.bsd_ct_ids.\
                filtered(lambda c: c.bsd_tu_ngay < ngay_ut < c.bsd_den_ngay)
            ck_ttth = item_ttth[0].bsd_chiet_khau_id if item_ttth else False
        if dot_mb.bsd_ck_ttn_id:
            item_ttn = dot_mb.bsd_ck_ttn_id.bsd_ct_ids.\
                filtered(lambda c: c.bsd_tu_ngay < ngay_ut < c.bsd_den_ngay)
            ck_ttn = item_ttn[0].bsd_chiet_khau_id if item_ttn else False
        # lấy các đợt thanh toán trước hạn
        dot_tt = hd_ban.bsd_ltt_ids\
            .filtered(lambda t: t.bsd_ngay_hh_tt and ngay_ut < t.bsd_ngay_hh_tt and t.bsd_loai=='dtt')\
            .sorted('bsd_stt')

        _logger.debug("chiết khấu")
        _logger.debug(ck_ttth)
        _logger.debug(ck_ttn)

        doc['khach_hang'] = {
            'name': khach_hang.name,
            'cmnd': khach_hang.bsd_cmnd,
            'mobile': khach_hang.mobile,
            'email': khach_hang.email,
            'dia_chi': khach_hang.bsd_dia_chi_lh,
            'so_can_ho': hd_ban.bsd_unit_id.bsd_ten_unit,
            'hop_dong': hd_ban.bsd_unit_id.bsd_ma_unit + " - " + hd_ban.bsd_ma_hd_ban,
        }
        # dữ liệu thanh toán nhanh
        doc['ck_ttn'] = {}
        if ck_ttn:
            doc['ck_ttn'] = {
                'bsd_ten_ck': ck_ttn.bsd_ten_ck,
                'bsd_tu_ngay': ck_ttn.bsd_tu_ngay.strftime("%d/%m/%Y"),
                'bsd_den_ngay': ck_ttn.bsd_den_ngay.strftime("%d/%m/%Y"),
                'bsd_gia_truoc_thue': hd_ban.bsd_gia_truoc_thue,
                'bsd_tl_tt': ck_ttn.bsd_tl_tt,
                'bsd_tl_ck': ck_ttn.bsd_tl_ck,
                'bsd_tong_ck': hd_ban.bsd_gia_truoc_thue * ck_ttn.bsd_tl_ck / 100
            }
        # Kiểm tra điều kiện thanh toán nhanh
        if doc['ck_ttn']:
            if data['bsd_tien_ut'] < doc['ck_ttn']['bsd_gia_truoc_thue'] * doc['ck_ttn']['bsd_tl_tt'] / 100:
                doc['ck_ttn']['bsd_tong_ck'] = 0
        # dữ liệu thanh toán trước hạn theo từng đợt
        doc['ck_ttth'] = []
        tong_tien_ck_ttth = 0
        if not dot_tt or not ck_ttth:
            pass
        else:
            so_tien_ut_can_tru = data['bsd_tien_ut']
            if data['bsd_tien_ut'] < dot_tt[0].bsd_tien_dot_tt:
                bsd_tien_tt = data['bsd_tien_ut']
                bsd_so_ngay_th = (dot_tt[0].bsd_ngay_hh_tt - ngay_ut).days
                bsd_tl_ck_dot = ck_ttth.bsd_tl_ck * bsd_so_ngay_th
                bsd_tien_ck = bsd_tien_tt * bsd_tl_ck_dot / 100
                tong_tien_ck_ttth += bsd_tien_ck
                doc['ck_ttth'].append({
                    'bsd_stt': dot_tt[0].bsd_stt,
                    'bsd_ten_dtt': dot_tt[0].bsd_ten_dtt,
                    'bsd_ngay_hh_tt': dot_tt[0].bsd_ngay_hh_tt.strftime("%d/%m/%Y"),
                    'bsd_ngay_tt': ngay_ut.strftime("%d/%m/%Y"),
                    'bsd_so_ngay_th': bsd_so_ngay_th,
                    'bsd_tien_dot_tt': dot_tt[0].bsd_tien_phai_tt,
                    'bsd_tl_ck_dot': float_repr(bsd_tl_ck_dot, precision_digits=3),
                    'bsd_tien_ck': bsd_tien_ck,
                    'bsd_tien_tt': bsd_tien_tt,
                })
            else:
                for dot in dot_tt:
                    so_tien_ut_can_tru -= dot.bsd_tien_dot_tt
                    if so_tien_ut_can_tru >= 0:
                        bsd_tien_tt = dot.bsd_tien_dot_tt
                    else:
                        bsd_tien_tt = abs(so_tien_ut_can_tru)
                        bsd_so_ngay_th = (dot.bsd_ngay_hh_tt - ngay_ut).days
                        bsd_tl_ck_dot = ck_ttth.bsd_tl_ck * bsd_so_ngay_th
                        bsd_tien_ck = bsd_tien_tt * bsd_tl_ck_dot / 100
                        tong_tien_ck_ttth += bsd_tien_ck
                        doc['ck_ttth'].append({
                            'bsd_stt': dot.bsd_stt,
                            'bsd_ten_dtt': dot.bsd_ten_dtt,
                            'bsd_ngay_hh_tt': dot.bsd_ngay_hh_tt.strftime("%d/%m/%Y"),
                            'bsd_ngay_tt': ngay_ut.strftime("%d/%m/%Y"),
                            'bsd_so_ngay_th': bsd_so_ngay_th,
                            'bsd_tien_dot_tt': dot.bsd_tien_phai_tt,
                            'bsd_tl_ck_dot': float_repr(bsd_tl_ck_dot, precision_digits=3),
                            'bsd_tien_ck': bsd_tien_ck,
                            'bsd_tien_tt': bsd_tien_tt,
                        })
                        break
                    bsd_so_ngay_th = (dot.bsd_ngay_hh_tt - ngay_ut).days
                    bsd_tl_ck_dot = ck_ttth.bsd_tl_ck * bsd_so_ngay_th
                    bsd_tien_ck = bsd_tien_tt * bsd_tl_ck_dot / 100
                    tong_tien_ck_ttth += bsd_tien_ck
                    doc['ck_ttth'].append({
                        'bsd_stt': dot.bsd_stt,
                        'bsd_ten_dtt': dot.bsd_ten_dtt,
                        'bsd_ngay_hh_tt': dot.bsd_ngay_hh_tt.strftime("%d/%m/%Y"),
                        'bsd_ngay_tt': ngay_ut.strftime("%d/%m/%Y"),
                        'bsd_so_ngay_th': bsd_so_ngay_th,
                        'bsd_tien_dot_tt': dot.bsd_tien_dot_tt,
                        'bsd_tl_ck_dot': float_repr(bsd_tl_ck_dot, precision_digits=3),
                        'bsd_tien_ck': bsd_tien_ck,
                        'bsd_tien_tt': bsd_tien_tt,
                    })

        doc['doc_ids'] = data['ids']
        doc['doc_model'] = data['model']
        doc['bsd_ngay_ut'] = ngay_ut.strftime("%d/%m/%Y")
        doc['bsd_tien_ut'] = data['bsd_tien_ut']
        doc['bsd_tl_ck_ttth'] = ck_ttth.bsd_tl_ck if ck_ttth else 0
        doc['currency_id'] = currency_id
        doc['tong_tien_ck_ttn'] = doc['ck_ttn']['bsd_tong_ck'] if doc['ck_ttn']else 0
        doc['tong_tien_ck_ttth'] = tong_tien_ck_ttth
        doc['tong_tien_ck'] = tong_tien_ck_ttth + doc['ck_ttn']['bsd_tong_ck'] if doc['ck_ttn']else 0
        _logger.debug(doc)
        return doc
