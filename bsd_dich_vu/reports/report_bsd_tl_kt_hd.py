# -*- coding:utf-8 -*-

from odoo import api, models, fields
import logging
import datetime
_logger = logging.getLogger(__name__)


class BsdWizardReportTLKTHD(models.TransientModel):
    _name = 'bsd.tl_kt_hd.report.wizard'
    _description = 'Chọn mẫu in Bàn giao giấy tờ'

    def _get_tl_kt_hd(self):
        bg = self.env['bsd.tl_kt_hd'].browse(self._context.get('active_ids', []))
        return bg

    bsd_tl_kt_hd_id = fields.Many2one('bsd.tl_kt_hd', string="Bàn giao giấy tờ", default=_get_tl_kt_hd, readonly=True)
    bsd_mau_in = fields.Selection([('bsd_mau_in_tl_kt_hd_html', 'Bàn giao giấy tờ(html)'),
                                   ('bsd_mau_in_tl_kt_hd', 'Bàn giao giấy tờ')], string="Mẫu in", required=True,
                                  default='bsd_mau_in_tl_kt_hd_html')

    def action_in(self):
        """Call when button 'Get Report' clicked.
        """
        data = {
            'ids': self.bsd_tl_kt_hd_id.ids,
            'model': self.bsd_tl_kt_hd_id._name,
        }
        if not self.bsd_tl_kt_hd_id.bsd_ngay_in:
            self.bsd_tl_kt_hd_id.write({
                'bsd_ngay_in': fields.Datetime.now(),
                'bsd_nguoi_in_id': self.env.uid
            })
        ref_id = 'bsd_dich_vu.' + self.bsd_mau_in
        return self.env.ref(ref_id).report_action(self, data=data)


class ReportBsdBGSP(models.AbstractModel):
    _name = 'report.bsd_dich_vu.bsd_tl_kt_hd_view'

    @api.model
    def _get_report_values(self, docids, data=None):
        return {
            'doc_ids': data['ids'],
            'doc_model': data['model'],
            'docs': self.env['bsd.tl_kt_hd'].browse(data['ids']),
        }