# -*- coding:utf-8 -*-

from odoo import api, models, fields
import logging
from num2words import num2words
import datetime
from dateutil import tz
_logger = logging.getLogger(__name__)


class BsdWizardReportGCTC(models.TransientModel):
    _name = 'bsd.gc_tc.report.wizard'
    _description = 'Chọn mẫu in giữ chỗ thiện chí'

    def _get_gc_tc(self):
        gc_tc = self.env['bsd.gc_tc'].browse(self._context.get('active_ids', []))
        return gc_tc

    bsd_gc_tc_id = fields.Many2one('bsd.gc_tc', string="Giữ chỗ thiện chí", default=_get_gc_tc, readonly=True)
    bsd_mau_in = fields.Selection([('bsd_mau_in_gc_tc_chuan', 'Giữ chỗ thiện chí'),
                                   ('bsd_mau_in_gc_tc_chuan_html', 'Giữ chỗ thiện chí (html)')], string="Mẫu in",
                                  required=True,
                                  default='bsd_mau_in_gc_tc_chuan')

    def action_in(self):
        """Call when button 'Get Report' clicked.
        """
        data = {
            'ids': self.bsd_gc_tc_id.ids,
            'model': self.bsd_gc_tc_id._name,
        }
        ref_id = 'bsd_kinh_doanh.' + self.bsd_mau_in
        return self.env.ref(ref_id).report_action(self, data=data)


class ReportBsdGCTG(models.AbstractModel):
    _name = 'report.bsd_kinh_doanh.bsd_gc_tc_view'

    @api.model
    def _get_report_values(self, docids, data=None):
        gc_tc = self.env['bsd.gc_tc'].browse(data['ids'])
        tien_gc_tc = num2words(gc_tc.bsd_du_an_id.bsd_tien_gc, lang='vi_VN') + ' ' + 'đồng'
        ngay_hien_tai = datetime.datetime.now()
        from_zone = tz.gettz('UTC')
        to_zone = tz.gettz('Asia/Ho_Chi_Minh')
        ngay_hien_tai = ngay_hien_tai.replace(tzinfo=from_zone)
        ngay_hien_tai = ngay_hien_tai.astimezone(to_zone)
        _logger.debug(ngay_hien_tai)
        return {
            'doc_ids': data['ids'],
            'doc_model': data['model'],
            'docs': gc_tc,
            'tien_gc_tc_chu': tien_gc_tc,
            'ngay_hien_tai': ngay_hien_tai.strftime("%d/%m/%y")
        }