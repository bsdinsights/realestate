# -*- coding:utf-8 -*-

from odoo import api, models, fields
import logging
import datetime
_logger = logging.getLogger(__name__)


class BsdWizardReportTBNT(models.TransientModel):
    _name = 'bsd.tb_nt.report.wizard'
    _description = 'Chọn mẫu in thông báo bàn giao'

    def _get_tbnt(self):
        hdb = self.env['bsd.tb_nt'].browse(self._context.get('active_ids', []))
        return hdb

    bsd_tb_nt_id = fields.Many2one('bsd.tb_nt', string="Thông báo nghiệm thu", default=_get_tbnt, readonly=True)
    bsd_mau_in = fields.Selection([('bsd_mau_in_tb_nt_html', 'Thông báo nghiệm thu (html)'),
                                   ('bsd_mau_in_tb_nt', 'Thông báo nghiệm thu')], string="Mẫu in", required=True,
                                  default='bsd_mau_in_tb_nt_html')

    def action_in(self):
        """Call when button 'Get Report' clicked.
        """
        data = {
            'ids': self.bsd_tb_nt_id.ids,
            'model': self.bsd_tb_nt_id._name,
        }
        self.bsd_tb_nt_id.write({
            'bsd_ngay_in': datetime.datetime.now(),
            'bsd_nguoi_in_id': self.env.uid,
        })
        ref_id = 'bsd_dich_vu.' + self.bsd_mau_in
        return self.env.ref(ref_id).report_action(self, data=data)


class ReportBsdTBNT(models.AbstractModel):
    _name = 'report.bsd_dich_vu.bsd_tb_nt_view'

    @api.model
    def _get_report_values(self, docids, data=None):
        _logger.debug("Chạy tới đây")
        return {
            'doc_ids': data['ids'],
            'doc_model': data['model'],
            'docs': self.env['bsd.tb_nt'].browse(data['ids']),
        }