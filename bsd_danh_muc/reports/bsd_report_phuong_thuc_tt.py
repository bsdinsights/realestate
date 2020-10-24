# -*- coding:utf-8 -*-

from odoo import api, models, fields
from odoo.exceptions import UserError
import logging
import datetime
import calendar
from dateutil import tz
_logger = logging.getLogger(__name__)


class ReportLTT(models.AbstractModel):
    _name = 'report.bsd_danh_muc.bsd_ltt_view'

    def _tao_lich_tt(self, cs_tt, ngay_hh_tt):
        def add_months(sourcedate, months):
            month = sourcedate.month - 1 + months
            year = sourcedate.year + month // 12
            month = month % 12 + 1
            day = min(sourcedate.day, calendar.monthrange(year, month)[1])
            return datetime.date(year, month, day)

        # tạo biến cục bộ
        stt = 0  # Đánh số thứ tự record đợt thanh toán
        dot_tt_ids = cs_tt.bsd_ct_ids
        # biến chứa lịch thanh toán
        list_ltt = []
        check_dot_ky_hd = False
        check_dot_cuoi = False
        check_dot_pql = False
        check_dot_pbt = False
        # Tạo các đợt thanh toán
        for dot in dot_tt_ids.sorted('bsd_stt'):
            # Tạo dữ liệu đợt cố định
            if dot.bsd_cach_tinh == 'cd' and not dot.bsd_dot_cuoi:
                dot_cd = dot
                stt += 1
                check_dot_ky_hd = dot_cd.bsd_dot_ky_hd
                check_dot_cuoi = dot_cd.bsd_dot_cuoi
                check_dot_pbt = dot_cd.bsd_tinh_pbt
                check_dot_pql = dot_cd.bsd_tinh_pql
                # Ngày hết hạn thanh toán
                ngay_hh_tt = dot_cd.bsd_ngay_cd
                # Tỷ lệ thanh toán của đợt
                list_ltt.append((
                    'Đợt {0}'.format(stt),
                    ngay_hh_tt.strftime("%d/%m/%y"),
                    '{0} %'.format(dot_cd.bsd_tl_tt).replace('.', ','),
                    check_dot_ky_hd,
                    check_dot_cuoi,
                    check_dot_pql,
                    check_dot_pbt
                ))
            # Tạo dữ liệu đợt tự động
            elif dot.bsd_cach_tinh == 'td':
                dot_td = dot
                ngay_hh_tt_td = ngay_hh_tt
                list_ngay_hh_tt_td = []
                if dot_td.bsd_lap_lai == '1':
                    for dot_i in range(0, dot_td.bsd_so_dot):
                        if dot_td.bsd_tiep_theo == 'ngay':
                            ngay_hh_tt_td += datetime.timedelta(days=dot_td.bsd_so_ngay)
                        else:
                            ngay_hh_tt_td = add_months(ngay_hh_tt_td, dot_td.bsd_so_thang)
                        list_ngay_hh_tt_td.append(ngay_hh_tt_td)
                else:
                    if dot_td.bsd_tiep_theo == 'ngay':
                        ngay_hh_tt_td += datetime.timedelta(days=dot_td.bsd_so_ngay)
                    else:
                        ngay_hh_tt_td = add_months(ngay_hh_tt_td, dot_td.bsd_so_thang)
                    list_ngay_hh_tt_td.append(ngay_hh_tt_td)
                # cộng thời gian gia hạn cuối của đợt tự động
                list_ngay_hh_tt_td[-1] += datetime.timedelta(days=dot_td.bsd_ngay_gh)
                # Gán lại ngày cuối cùng tự động thanh toán
                ngay_hh_tt = list_ngay_hh_tt_td[-1]
                # kiểm tra đợt đầu tiên tự động
                stt_td_đau_tien = stt + 1
                check_dot_ky_hd = dot_td.bsd_dot_ky_hd
                check_dot_cuoi = dot_td.bsd_dot_cuoi
                check_dot_pbt = dot_td.bsd_tinh_pbt
                check_dot_pql = dot_td.bsd_tinh_pql
                # Gán lich
                for ngay in list_ngay_hh_tt_td:
                    stt += 1
                    if dot_td.bsd_ngay_thang > 0:
                        last_day = calendar.monthrange(ngay.year, ngay.month)[1]

                        if dot_td.bsd_ngay_thang > last_day:
                            ngay = ngay.replace(day=last_day)
                        else:
                            ngay = ngay.replace(day=dot_td.bsd_ngay_thang)
                    if stt_td_đau_tien == stt:
                        list_ltt.append((
                            'Đợt {0}'.format(stt),
                            ngay.strftime("%d/%m/%y"),
                            '{0} %'.format(dot_td.bsd_tl_tt).replace('.', ','),
                            check_dot_ky_hd,
                            check_dot_cuoi,
                            check_dot_pql,
                            check_dot_pbt
                        ))
                    else:
                        list_ltt.append((
                            'Đợt {0}'.format(stt),
                            ngay.strftime("%d/%m/%y"),
                            '{0} %'.format(dot_td.bsd_tl_tt).replace('.', ','),
                            False,
                            False,
                            False,
                            False
                        ))

            # Tạo đợt thanh toán theo dự kiến bàn giao
            elif dot.bsd_cach_tinh == 'dkbg':
                dot_dkbg = dot
                ngay_hh_tt_dkbg = cs_tt.bsd_du_an_id.bsd_ngay_dkbg or False
                stt += 1
                check_dot_ky_hd = dot_dkbg.bsd_dot_ky_hd
                check_dot_cuoi = dot_dkbg.bsd_dot_cuoi
                check_dot_pbt = dot_dkbg.bsd_tinh_pbt
                check_dot_pql = dot_dkbg.bsd_tinh_pql
                # cập nhật lại ngày hết hạn thanh toán
                ngay_hh_tt = ngay_hh_tt_dkbg

                list_ltt.append((
                    'Đợt {0}'.format(stt),
                    ngay_hh_tt.strftime("%d/%m/%y"),
                    '{0} %'.format(dot_dkbg.bsd_tl_tt).replace('.', ','),
                    check_dot_ky_hd,
                    check_dot_cuoi,
                    check_dot_pql,
                    check_dot_pbt
                ))

            # Tạo đợt thanh toán cuối
            elif dot.bsd_dot_cuoi:
                dot_cuoi = dot
                stt += 1
                check_dot_ky_hd = dot_cuoi.bsd_dot_ky_hd
                check_dot_cuoi = dot_cuoi.bsd_dot_cuoi
                check_dot_pbt = dot_cuoi.bsd_tinh_pbt
                check_dot_pql = dot_cuoi.bsd_tinh_pql
                list_ltt.append((
                    'Đợt {0}'.format(stt),
                    None,
                    '{0} %'.format(dot_cuoi.bsd_tl_tt).replace('.', ','),
                    check_dot_ky_hd,
                    check_dot_cuoi,
                    check_dot_pql,
                    check_dot_pbt
                ))
        return list_ltt

    @api.model
    def _get_report_values(self, docids, data=None):
        cs_tt = self.env['bsd.cs_tt'].browse(docids)
        ngay_hien_tai = datetime.datetime.now()
        from_zone = tz.gettz('UTC')
        to_zone = tz.gettz(self._context['tz'])
        ngay_hien_tai = ngay_hien_tai.replace(tzinfo=from_zone)
        ngay_hien_tai = ngay_hien_tai.astimezone(to_zone)
        res = {
            'docs': cs_tt,
            'ngay_ht': ngay_hien_tai.strftime("%d/%m/%y"),
            'list_tt': self._tao_lich_tt(cs_tt, ngay_hien_tai)
        }
        _logger.debug("kết quả in")
        _logger.debug(res)
        return res
