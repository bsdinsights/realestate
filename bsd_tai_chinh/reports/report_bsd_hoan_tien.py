# -*- coding:utf-8 -*-

from odoo import api, models, fields
from num2words import num2words
import logging
import datetime
from dateutil import tz
_logger = logging.getLogger(__name__)


class BsdWizardReportHoanTien(models.TransientModel):
    _name = 'bsd.hoan_tien.report.wizard'
    _description = 'Chọn mẫu in Hoàn tiền'

    def _get_pt(self):
        pt = self.env['bsd.hoan_tien'].browse(self._context.get('active_ids', []))
        return pt

    bsd_hoan_tien_id = fields.Many2one('bsd.hoan_tien', string="Hoàn tiền", default=_get_pt, readonly=True)
    bsd_mau_in = fields.Selection([('bsd_mau_in_hoan_tien_chuan', 'Hoàn tiền'),
                                   ('bsd_mau_in_hoan_tien_chuan_html', 'Hoàn tiền (html)')], string="Mẫu in", required=True,
                                  default='bsd_mau_in_hoan_tien_chuan')

    def action_in(self):
        """Call when button 'Get Report' clicked.
        """
        data = {
            'ids': self.bsd_hoan_tien_id.ids,
            'model': self.bsd_hoan_tien_id._name,
        }
        ref_id = 'bsd_tai_chinh.' + self.bsd_mau_in
        return self.env.ref(ref_id).report_action(self, data=data)


class ReportBsdHoanTien(models.AbstractModel):
    _name = 'report.bsd_tai_chinh.bsd_hoan_tien_view'

    @api.model
    def _get_report_values(self, docids, data=None):
        hoan_tien = self.env['bsd.hoan_tien'].browse(data['ids'])
        from_zone = tz.gettz('UTC')
        to_zone = tz.gettz(self._context['tz'])
        ngay_hoan_tien = hoan_tien.bsd_ngay_ct.replace(tzinfo=from_zone)
        ngay_hoan_tien = ngay_hoan_tien.astimezone(to_zone)

        ngay_ht = datetime.datetime.now()
        ngay_ht = ngay_ht.replace(tzinfo=from_zone)
        ngay_ht = ngay_ht.astimezone(to_zone)

        ly_do = ''
        if hoan_tien.bsd_loai == 'gc_tc':
            ly_do = 'Hoàn tiền giữ chỗ thiện chí'
        if hoan_tien.bsd_loai == 'giu_cho':
            ly_do = 'Hoàn tiền giữ chỗ'
        if hoan_tien.bsd_loai == 'tl_dc':
            ly_do = 'Hoàn tiền đặt cọc'
        if hoan_tien.bsd_loai == 'phieu_thu':
            ly_do = 'Hoàn tiền phiếu thu'
        if hoan_tien.bsd_loai in ['tl_ttdc', 'tl_hd']:
            ly_do = 'Hoàn tiền đợt thanh toán'

        tien_chu = num2words(hoan_tien.bsd_tien, lang='vi_VN').capitalize() + ' ' + 'đồng'
        return {
            'doc_ids': data['ids'],
            'doc_model': data['model'],
            'docs': hoan_tien,
            'ngay_pc': ngay_hoan_tien,
            'ngay_ht': ngay_ht,
            'tien_chu': tien_chu,
            'ly_do': ly_do,
        }