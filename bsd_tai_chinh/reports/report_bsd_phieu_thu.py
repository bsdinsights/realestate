# -*- coding:utf-8 -*-

from odoo import api, models, fields
from num2words import num2words
import logging
import datetime
from dateutil import tz
_logger = logging.getLogger(__name__)


class BsdWizardReportPhieuThu(models.TransientModel):
    _name = 'bsd.phieu_thu.report.wizard'
    _description = 'Chọn mẫu in Phiếu thu'

    def _get_pt(self):
        pt = self.env['bsd.phieu_thu'].browse(self._context.get('active_ids', []))
        return pt

    bsd_phieu_thu_id = fields.Many2one('bsd.phieu_thu', string="Phiếu thu", default=_get_pt, readonly=True)
    bsd_mau_in = fields.Selection([('bsd_mau_in_phieu_thu_chuan', 'Phiếu thu'),
                                   ('bsd_mau_in_phieu_thu_chuan_html', 'Phiếu thu (html)')], string="Mẫu in", required=True,
                                  default='bsd_mau_in_phieu_thu_chuan')

    def action_in(self):
        """Call when button 'Get Report' clicked.
        """
        data = {
            'ids': self.bsd_phieu_thu_id.ids,
            'model': self.bsd_phieu_thu_id._name,
        }
        ref_id = 'bsd_tai_chinh.' + self.bsd_mau_in
        return self.env.ref(ref_id).report_action(self, data=data)


class ReportBsdPhieuThu(models.AbstractModel):
    _name = 'report.bsd_tai_chinh.bsd_phieu_thu_view'

    @api.model
    def _get_report_values(self, docids, data=None):
        phieu_thu = self.env['bsd.phieu_thu'].browse(data['ids'])
        from_zone = tz.gettz('UTC')
        to_zone = tz.gettz(self._context['tz'])
        ngay_phieu_thu = phieu_thu.bsd_ngay_pt.replace(tzinfo=from_zone)
        ngay_phieu_thu = ngay_phieu_thu.astimezone(to_zone)

        ngay_ht = datetime.datetime.now()
        ngay_ht = ngay_ht.replace(tzinfo=from_zone)
        ngay_ht = ngay_ht.astimezone(to_zone)

        tien_chu = num2words(phieu_thu.bsd_tien_kh, lang='vi_VN').capitalize() + ' ' + 'đồng'
        return {
            'doc_ids': data['ids'],
            'doc_model': data['model'],
            'docs': phieu_thu,
            'ngay_pt': ngay_phieu_thu,
            'ngay_ht': ngay_ht,
            'tien_chu': tien_chu
        }