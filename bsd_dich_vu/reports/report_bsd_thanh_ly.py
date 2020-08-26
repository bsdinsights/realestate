# -*- coding:utf-8 -*-

from odoo import api, models, fields
import logging
import datetime
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
            'bsd_ngay_in': datetime.datetime.now(),
        })
        ref_id = 'bsd_dich_vu.' + self.bsd_mau_in
        return self.env.ref(ref_id).report_action(self, data=data)


class ReportBsdTBTL(models.AbstractModel):
    _name = 'report.bsd_dich_vu.bsd_thanh_ly_view'

    @api.model
    def _get_report_values(self, docids, data=None):
        return {
            'doc_ids': data['ids'],
            'doc_model': data['model'],
            'docs': self.env['bsd.thanh_ly'].browse(data['ids']),
        }