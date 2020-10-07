# -*- coding:utf-8 -*-

from odoo import api, models, fields
import logging
import datetime
from dateutil import tz
_logger = logging.getLogger(__name__)


class BsdWizardReportThanhLy(models.TransientModel):
    _name = 'bsd.tb_tt.report.wizard'
    _description = 'Chọn mẫu in thông báo thanh toán'

    def _get_tb_tt(self):
        tb_tt = self.env['bsd.tb_tt'].browse(self._context.get('active_ids', []))
        return tb_tt

    bsd_tb_tt_id = fields.Many2one('bsd.tb_tt', string="Thông báo", default=_get_tb_tt, readonly=True)
    bsd_mau_in = fields.Selection([('bsd_mau_in_tb_tt_html', 'Thông báo thanh toán (html)'),
                                   ('bsd_mau_in_tb_tt', 'Thông báo thanh toán'),
                                   ('bsd_mau_in_tb_tt_dot_cuoi_html', 'Thông báo thanh toán đợt cuối (html)')],
                                  string="Mẫu in", required=True,
                                  default='bsd_mau_in_tb_tt_html')

    def action_in(self):
        """Call when button 'Get Report' clicked.
        """
        data = {
            'ids': self.bsd_tb_tt_id.ids,
            'model': self.bsd_tb_tt_id._name,
        }
        self.bsd_tb_tt_id.write({
            'bsd_ngay_in': datetime.datetime.now(),
        })
        ref_id = 'bsd_dich_vu.' + self.bsd_mau_in
        return self.env.ref(ref_id).report_action(self, data=data)


class ReportBsdTBTTNN(models.AbstractModel):
    _name = 'report.bsd_dich_vu.bsd_tb_tt_view'

    @api.model
    def _get_report_values(self, docids, data=None):
        doc = self.env['bsd.tb_tt'].browse(data['ids'])
        ngay_ht = datetime.datetime.now()
        from_zone = tz.gettz('UTC')
        to_zone = tz.gettz(self._context['tz'])
        ngay_ht = ngay_ht.replace(tzinfo=from_zone)
        ngay_ht = ngay_ht.astimezone(to_zone)
        return {
            'doc_ids': data['ids'],
            'doc_model': data['model'],
            'docs': doc,
            'ngay_ht': ngay_ht,
        }


class ReportBsdTBTTNNDotCuoi(models.AbstractModel):
    _name = 'report.bsd_dich_vu.bsd_tb_tt_dot_cuoi_view'

    @api.model
    def _get_report_values(self, docids, data=None):
        doc = self.env['bsd.tb_tt'].browse(data['ids'])
        ngay_ht = datetime.datetime.now()
        from_zone = tz.gettz('UTC')
        to_zone = tz.gettz(self._context['tz'])
        ngay_ht = ngay_ht.replace(tzinfo=from_zone)
        ngay_ht = ngay_ht.astimezone(to_zone)
        return {
            'doc_ids': data['ids'],
            'doc_model': data['model'],
            'docs': doc,
            'ngay_ht': ngay_ht,
        }