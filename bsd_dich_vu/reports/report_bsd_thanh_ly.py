# -*- coding:utf-8 -*-

from odoo import api, models, fields
import logging
import datetime
from dateutil import tz
_logger = logging.getLogger(__name__)


class BsdWizardReportThanhLy(models.TransientModel):
    _name = 'bsd.thanh_ly.report.wizard'
    _description = 'Chọn mẫu in thanh lý'

    def _get_thanh_ly(self):
        thanh_ly = self.env['bsd.thanh_ly'].browse(self._context.get('active_ids', []))
        return thanh_ly

    bsd_thanh_ly_id = fields.Many2one('bsd.thanh_ly', string="Thanh lý", default=_get_thanh_ly, readonly=True)
    bsd_mau_in = fields.Selection([('bsd_mau_in_thanh_ly_html', 'Thanh lý (html)'),
                                   ('bsd_mau_in_thanh_ly', 'Thanh lý')], string="Mẫu in", required=True,
                                  default='bsd_mau_in_thanh_ly_html')

    def action_in(self):
        """Call when button 'Get Report' clicked.
        """
        data = {
            'ids': self.bsd_thanh_ly_id.ids,
            'model': self.bsd_thanh_ly_id._name,
        }
        self.bsd_thanh_ly_id.write({
            'bsd_ngay_in': datetime.date.today(),
            'bsd_nguoi_in_id': self.env.uid,
        })
        ref_id = 'bsd_dich_vu.' + self.bsd_mau_in
        return self.env.ref(ref_id).report_action(self, data=data)


class ReportBsdTBTL(models.AbstractModel):
    _name = 'report.bsd_dich_vu.bsd_thanh_ly_view'

    @api.model
    def _get_report_values(self, docids, data=None):
        doc = self.env['bsd.thanh_ly'].browse(data['ids'])
        ngay_tl = doc.bsd_ngay_tao
        from_zone = tz.gettz('UTC')
        to_zone = tz.gettz(self._context['tz'])
        ngay_tl = ngay_tl.replace(tzinfo=from_zone)
        ngay_tl = ngay_tl.astimezone(to_zone)
        bsd_chu_dt_id = doc.bsd_du_an_id.bsd_chu_dt_id
        chu_dt = bsd_chu_dt_id.name
        so_dkdn = bsd_chu_dt_id.bsd_so_gpkd
        noi_cap = bsd_chu_dt_id.bsd_noi_gpkd
        ngay_dkdn = bsd_chu_dt_id.bsd_ngay_gpkd
        dia_chi_lien_he = bsd_chu_dt_id.bsd_dia_chi_lh
        so_dt = bsd_chu_dt_id.phone
        nguoi_dd = bsd_chu_dt_id.bsd_nguoi_dd_id
        xung_ho = 'Ông' if nguoi_dd.bsd_gioi_tinh == 'nam' else 'Bà'
        nguoi_dai_dien = nguoi_dd.display_name
        chuc_vu = nguoi_dd.function
        ma_so_thue = bsd_chu_dt_id.vat
        kh = doc.bsd_khach_hang_id
        ten_kh = kh.display_name
        so_cmnd = kh.bsd_cmnd
        ngay_cmnd = kh.bsd_ngay_cap_cmnd
        noi_cmnd = kh.bsd_noi_cap_cmnd
        dia_chi_lh_kh = kh.bsd_dia_chi_lh
        dia_chi_tt_kh = kh.bsd_dia_chi_tt
        email = kh.email
        so_dt_kh = kh.mobile
        return {
            'doc_ids': data['ids'],
            'doc_model': data['model'],
            'docs': doc,
            'ngay_tl': ngay_tl,
            'chu_dt': chu_dt,
            'so_dkdn': so_dkdn,
            'noi_cap': noi_cap,
            'ngay_dkdn': ngay_dkdn,
            'dia_chi_tru_so': "",
            'dia_chi_lien_he': dia_chi_lien_he,
            'so_dt': so_dt,
            'xung_ho': xung_ho,
            'nguoi_dai_dien': nguoi_dai_dien,
            'chuc_vu': chuc_vu,
            'so_tk': "",
            'ngan_hang': "",
            'ma_so_thue': ma_so_thue,
            'ten_kh': ten_kh,
            'so_cmnd': so_cmnd,
            'ngay_cmnd': ngay_cmnd.strftime("%d/%m/%Y") if ngay_cmnd else None,
            'noi_cmnd': noi_cmnd,
            'dia_chi_lh_kh': dia_chi_lh_kh,
            'dia_chi_tt_kh': dia_chi_tt_kh,
            'email': email,
            'so_dt_kh': so_dt_kh
        }