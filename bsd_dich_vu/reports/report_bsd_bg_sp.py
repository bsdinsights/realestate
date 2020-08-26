# -*- coding:utf-8 -*-

from odoo import api, models, fields
import logging
import datetime
_logger = logging.getLogger(__name__)


class BsdWizardReportBGSP(models.TransientModel):
    _name = 'bsd.bg_sp.report.wizard'
    _description = 'Chọn mẫu in Bàn giao sản phẩm'

    def _get_bg_sp(self):
        bg = self.env['bsd.bg_sp'].browse(self._context.get('active_ids', []))
        return bg

    bsd_bg_sp_id = fields.Many2one('bsd.bg_sp', string="Bàn giao sản phẩm", default=_get_bg_sp, readonly=True)
    bsd_mau_in = fields.Selection([('bsd_mau_in_bg_sp_html', 'Bàn giao sản phẩm(html)'),
                                   ('bsd_mau_in_bg_sp', 'Bàn giao sản phẩm')], string="Mẫu in", required=True,
                                  default='bsd_mau_in_bg_sp_html')

    def action_in(self):
        """Call when button 'Get Report' clicked.
        """
        data = {
            'ids': self.bsd_bg_sp_id.ids,
            'model': self.bsd_bg_sp_id._name,
        }
        if not self.bsd_bg_sp_id.bsd_ngay_in:
            self.bsd_bg_sp_id.write({
                'bsd_ngay_in': fields.Datetime.now(),
                'bsd_nguoi_in_id': self.env.uid
            })
        ref_id = 'bsd_dich_vu.' + self.bsd_mau_in
        return self.env.ref(ref_id).report_action(self, data=data)


class ReportBsdBGSP(models.AbstractModel):
    _name = 'report.bsd_dich_vu.bsd_bg_sp_view'

    @api.model
    def _get_report_values(self, docids, data=None):
        return {
            'doc_ids': data['ids'],
            'doc_model': data['model'],
            'docs': self.env['bsd.bg_sp'].browse(data['ids']),
        }