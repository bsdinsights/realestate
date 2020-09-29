# -*- coding:utf-8 -*-

from odoo import api, models, fields
import logging
import datetime
from num2words import num2words
_logger = logging.getLogger(__name__)


class BsdWizardReportHopDong(models.TransientModel):
    _name = 'bsd.hd_ban.report.wizard'
    _description = 'Chọn mẫu in hợp đồng'

    def _get_hdb(self):
        hdb = self.env['bsd.hd_ban'].browse(self._context.get('active_ids', []))
        return hdb

    bsd_hd_ban_id = fields.Many2one('bsd.hd_ban', string="Hợp đồng bán", default=_get_hdb, readonly=True)
    bsd_mau_in = fields.Selection([('bsd_mau_in_hdb', 'Hợp đồng (html)'),
                                   ('bsd_mau_in_ttdc', 'Thỏa thuận đặt cọc (html)')], string="Mẫu in", required=True,
                                  default='bsd_mau_in_hdb')

    def action_in(self):
        """Call when button 'Get Report' clicked.
        """
        data = {
            'ids': self.bsd_hd_ban_id.ids,
            'model': self.bsd_hd_ban_id._name,
        }
        if self.bsd_mau_in == 'bsd_mau_in_hdb':
            if not self.bsd_hd_ban_id.bsd_ngay_in_hdb:
                self.bsd_hd_ban_id.write({
                    'bsd_ngay_in_hdb': datetime.datetime.now(),
                    'bsd_ngay_hh_khdb': datetime.datetime.now() + datetime.timedelta(days=self.bsd_hd_ban_id.bsd_du_an_id.bsd_hh_hd)
                })
        if self.bsd_mau_in == 'bsd_mau_in_ttdc':
            if not self.bsd_hd_ban_id.bsd_ngay_in_ttdc:
                self.bsd_hd_ban_id.write({
                    'bsd_ngay_in_ttdc': datetime.datetime.now(),
                    'bsd_ngay_hh_ttdc': datetime.datetime.now() + datetime.timedelta(
                        days=self.bsd_hd_ban_id.bsd_du_an_id.bsd_hh_hd)
                })
        ref_id = 'bsd_dich_vu.' + self.bsd_mau_in

        _logger.debug(ref_id)
        return self.env.ref(ref_id).report_action(self, data=data)


class ReportBsdHdBan(models.AbstractModel):
    _name = 'report.bsd_dich_vu.bsd_hd_ban_view'

    @api.model
    def _get_report_values(self, docids, data=None):
        _logger.debug("Chạy tới đây")
        return {
            'doc_ids': data['ids'],
            'doc_model': data['model'],
            'docs': self.env['bsd.hd_ban'].browse(data['ids']),
        }


class ReportBsdTTDC(models.AbstractModel):
    _name = 'report.bsd_dich_vu.bsd_ttdc_view'

    @api.model
    def _get_report_values(self, docids, data=None):
        doc = self.env['bsd.hd_ban'].browse(data['ids'])
        ngay_ht = datetime.datetime.now()
        ten_da = doc.bsd_du_an_id.bsd_ten_da
        dia_chi_da = doc.bsd_du_an_id.bsd_dia_chi
        ten_kh = doc.bsd_khach_hang_id.bsd_ten
        ngay_sinh_kh = doc.bsd_khach_hang_id.bsd_ngay_sinh
        so_cmnd = doc.bsd_khach_hang_id.bsd_cmnd
        dc_tt = doc.bsd_khach_hang_id.bsd_dia_chi_tt
        dc_lh = doc.bsd_khach_hang_id.bsd_dia_chi_lh
        so_dt = doc.bsd_khach_hang_id.mobile
        email_kh = doc.bsd_khach_hang_id.email
        ten_cty = doc.bsd_du_an_id.bsd_chu_dt_id.name
        dc_lh_cty = doc.bsd_du_an_id.bsd_chu_dt_id.bsd_dia_chi_lh
        so_dt_cty = doc.bsd_du_an_id.bsd_chu_dt_id.phone
        ms_thue_cty = doc.bsd_du_an_id.bsd_chu_dt_id.vat
        ngay_cap_vat = doc.bsd_du_an_id.bsd_chu_dt_id.bsd_ngay_vat
        nguoi_dd_cty = doc.bsd_du_an_id.bsd_chu_dt_id.bsd_nguoi_dd_id
        xung_ho = 'Ông' if nguoi_dd_cty.bsd_gioi_tinh == 'nam' else 'Bà'
        nguoi_dd = nguoi_dd_cty.bsd_ten
        chuc_vu = nguoi_dd_cty.function
        loai_sp = doc.bsd_unit_id.bsd_loai_sp_id.bsd_ten_nhom
        ma_sp = doc.bsd_unit_id.bsd_ten_unit
        dt_dat = doc.bsd_unit_id.bsd_dt_xd
        dt_xd = doc.bsd_unit_id.bsd_dt_sd
        gia_ban_chu = num2words(doc.bsd_tong_gia, lang='vi_VN') + ' ' + 'đồng'
        khuyen_mai_ids = doc.bsd_km_ids.mapped('bsd_khuyen_mai_id').mapped('bsd_ten_km')
        return {
            'doc_ids': data['ids'],
            'doc_model': data['model'],
            'docs': self.env['bsd.hd_ban'].browse(data['ids']),
            'ngay_ht': ngay_ht,
            'ten_da': ten_da,
            'dia_chi_da': dia_chi_da,
            'ten_kh': ten_kh,
            'ngay_sinh_kh': ngay_sinh_kh,
            'so_cmnd': so_cmnd,
            'dc_tt': dc_tt,
            'dc_lh': dc_lh,
            'so_dt': so_dt,
            'email_kh': email_kh,
            'ten_cty': ten_cty,
            'dc_lh_cty': dc_lh_cty,
            'so_dt_cty': so_dt_cty,
            'ms_thue_cty': ms_thue_cty,
            'ngay_cap_vat': ngay_cap_vat,
            'xung_ho': xung_ho,
            'nguoi_dd': nguoi_dd,
            'chuc_vu': chuc_vu,
            'loai_sp': loai_sp,
            'ma_sp': ma_sp,
            'dt_dat': dt_dat,
            'dt_xd': dt_xd,
            'gia_ban_chu': gia_ban_chu,
            'khuyen_mai_ids': khuyen_mai_ids
        }

