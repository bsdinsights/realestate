# -*- coding:utf-8 -*-

from odoo import api, models, fields
import logging
import datetime
_logger = logging.getLogger(__name__)


class BsdWizardReportTBTL(models.TransientModel):
    _name = 'bsd.tb_tl.report.wizard'
    _description = 'Chọn mẫu in thông báo thanh lý'

    def _get_tbbg(self):
        bg = self.env['bsd.tb_tl'].browse(self._context.get('active_ids', []))
        return bg

    bsd_tb_tl_id = fields.Many2one('bsd.tb_tl', string="Thông báo thanh lý", default=_get_tbbg, readonly=True)
    bsd_mau_in = fields.Selection([('bsd_mau_in_tb_tl_html', 'Thông báo thanh lý (html)'),
                                   ('bsd_mau_in_tb_tl', 'Thông báo thanh lý')], string="Mẫu in", required=True,
                                  default='bsd_mau_in_tb_tl_html')

    def action_in(self):
        """Call when button 'Get Report' clicked.
        """
        data = {
            'ids': self.bsd_tb_tl_id.ids,
            'model': self.bsd_tb_tl_id._name,
        }
        self.bsd_tb_tl_id.write({
            'bsd_ngay_in': datetime.datetime.now(),
        })
        ref_id = 'bsd_dich_vu.' + self.bsd_mau_in
        return self.env.ref(ref_id).report_action(self, data=data)


class ReportBsdTBTL(models.AbstractModel):
    _name = 'report.bsd_dich_vu.bsd_tb_tl_view'

    @api.model
    def _get_report_values(self, docids, data=None):
        return {
            'doc_ids': data['ids'],
            'doc_model': data['model'],
            'docs': self.env['bsd.tb_tl'].browse(data['ids']),
        }