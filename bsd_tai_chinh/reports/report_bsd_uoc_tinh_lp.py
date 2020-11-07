# -*- coding:utf-8 -*-

from odoo import api, models, fields
from odoo.exceptions import UserError
from odoo.tools.float_utils import float_round,float_repr
import logging
import datetime
_logger = logging.getLogger(__name__)


class ReportBsdUocTinhLaiPhat(models.AbstractModel):
    _name = 'report.bsd_tai_chinh.bsd_uoc_tinh_lp_view'

    @api.model
    def _get_report_values(self, docids, data=None,):
        doc = {}
        # lấy thông tin hợp đồng căn hộ
        hd_ban = self.env['bsd.hd_ban'].browse(data['ids'])
        unit = hd_ban.bsd_unit_id
        ngay_ut = datetime.datetime.strptime(data['bsd_ngay_ut'], '%Y-%m-%d').date()
        cs_tt = hd_ban.bsd_cs_tt_id
        tong_tp = 0
        khach_hang = hd_ban.bsd_khach_hang_id
        doc.update({
            'currency_id': hd_ban.currency_id,
            'hd_ban': {
                'ten_hd': unit.bsd_ma_unit + '-' + hd_ban.bsd_ma_hd_ban,
                'so_can_ho': unit.bsd_ten_unit,
                'lich_tt': cs_tt.bsd_ten_cstt,
                'ngay_ut': ngay_ut.strftime("%d/%m/%Y"),
                'lai_phat': cs_tt.bsd_lai_phat_tt_id.bsd_lai_phat,
                'tien_td': cs_tt.bsd_lai_phat_tt_id.bsd_tien_td,
                'tl_td': cs_tt.bsd_lai_phat_tt_id.bsd_tl_td,
                'tong_tp': tong_tp,
            },
            'khach_hang': {
                'ten': khach_hang.display_name,
                'so_cmnd': khach_hang.bsd_cmnd,
                'so_dt': khach_hang.mobile,
                'email': khach_hang.email,
                'dia_chi': khach_hang.bsd_dia_chi_lh,
            },
        })
        # Load các đợt chưa thanh toán của hợp đồng
        dot_tt_ids = hd_ban.bsd_ltt_ids\
            .filtered(lambda d: d.bsd_thanh_toan != 'da_tt' and d.bsd_ngay_hh_tt)\
            .sorted('bsd_stt')
        tong_tien_chua_tt = 0
        tong_tien_phat = 0
        lich_tt = []
        for dot_tt in dot_tt_ids:
            # Kiểm tra ngày làm mốc tính lãi phạt
            han_tinh_phat = dot_tt.bsd_ngay_hh_tt
            if dot_tt.bsd_tinh_phat == 'nah':
                han_tinh_phat = dot_tt.bsd_ngay_ah
            # Số ngày tính lãi phạt
            so_ngay_nam = cs_tt.bsd_lai_phat_tt_id.bsd_so_ngay_nam
            if ngay_ut > han_tinh_phat:
                # Số ngày tính phạt
                so_ngay_tp = (ngay_ut - han_tinh_phat).days
                # Tính lãi phạt
                tien_phat = float_round(dot_tt.bsd_tien_phai_tt * (dot_tt.bsd_lai_phat/100 / so_ngay_nam) * so_ngay_tp, 0)
                # Kiểm tra lãi phạt đã vượt lãi phạt tối đa của đợt chưa
                tong_tien_phat = dot_tt.bsd_tien_phat + tien_phat
                if dot_tt.bsd_tien_td == 0 and dot_tt.bsd_tl_td != 0:
                    tien_phat_toi_da = dot_tt.bsd_tien_dot_tt * dot_tt.bsd_tl_td / 100
                    if tong_tien_phat > tien_phat_toi_da:
                        tien_phat = tien_phat_toi_da - dot_tt.bsd_tien_phat
                elif dot_tt.bsd_tien_td != 0 and dot_tt.bsd_tl_td == 0:
                    tien_phat_toi_da = dot_tt.bsd_tien_td
                    if tong_tien_phat > tien_phat_toi_da:
                        tien_phat = tien_phat_toi_da - dot_tt.bsd_tien_phat
                elif dot_tt.bsd_tien_td != 0 and dot_tt.bsd_tl_td != 0:
                    tien_phat_toi_da_1 = dot_tt.bsd_tien_dot_tt * dot_tt.bsd_tl_td / 100
                    tien_phat_toi_da_2 = dot_tt.bsd_tien_td
                    tien_phat_toi_da = tien_phat_toi_da_1 if tien_phat_toi_da_1 < tien_phat_toi_da_2 else tien_phat_toi_da_2
                    if tong_tien_phat > tien_phat_toi_da:
                        tien_phat = tien_phat_toi_da - dot_tt.bsd_tien_phat
            else:
                so_ngay_tp = 0
                tien_phat = 0
            tong_tien_chua_tt += dot_tt.bsd_tien_phai_tt
            lich_tt.append({
                'stt': dot_tt.bsd_stt,
                'ten': dot_tt.bsd_ten_dtt,
                'trang_thai': 'Chưa TT' if dot_tt.bsd_thanh_toan == 'chua_tt' else 'Đang TT',
                'han_tt': dot_tt.bsd_ngay_hh_tt.strftime("%d/%m/%Y"),
                'so_ngay_qh': so_ngay_tp,
                'tien_dot': dot_tt.bsd_tien_dot_tt,
                'tien_mg': 0,
                'tien_phai_tt': dot_tt.bsd_tien_phai_tt,
                'tien_phat_truoc': dot_tt.bsd_tien_phat,
                'tien_phat': tien_phat,
                'tong_tien_phat': dot_tt.bsd_tien_phat + tien_phat,
            })
        for d in lich_tt:
            tong_tien_phat += d['tong_tien_phat']
        doc.update({
            'lich_tt': lich_tt,
            'tong_tien_chua_tt': tong_tien_chua_tt,
            'tong_tien_phat': tong_tien_phat,
            'tong_tien': tong_tien_chua_tt + tong_tien_phat
        })
        _logger.debug(doc)
        return doc
