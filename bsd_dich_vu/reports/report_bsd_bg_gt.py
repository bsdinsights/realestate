# -*- coding:utf-8 -*-

from odoo import api, models, fields
import logging
import datetime
_logger = logging.getLogger(__name__)


class BsdWizardReportBGGT(models.TransientModel):
    _name = 'bsd.bg_gt.report.wizard'
    _description = 'Chọn mẫu in Bàn giao giấy tờ'

    def _get_bg_gt(self):
        bg = self.env['bsd.bg_gt'].browse(self._context.get('active_ids', []))
        return bg

    bsd_bg_gt_id = fields.Many2one('bsd.bg_gt', string="Bàn giao giấy tờ", default=_get_bg_gt, readonly=True)
    bsd_mau_in = fields.Selection([('bsd_mau_in_bg_gt_html', 'Bàn giao giấy tờ(html)'),
                                   ('bsd_mau_in_bg_gt', 'Bàn giao giấy tờ')], string="Mẫu in", required=True,
                                  default='bsd_mau_in_bg_gt_html')

    def action_in(self):
        """Call when button 'Get Report' clicked.
        """
        data = {
            'ids': self.bsd_bg_gt_id.ids,
            'model': self.bsd_bg_gt_id._name,
        }
        if not self.bsd_bg_gt_id.bsd_ngay_in:
            self.bsd_bg_gt_id.write({
                'bsd_ngay_in': fields.Datetime.now(),
                'bsd_nguoi_in_id': self.env.uid
            })
        ref_id = 'bsd_dich_vu.' + self.bsd_mau_in
        return self.env.ref(ref_id).report_action(self, data=data)


class ReportBsdBGSP(models.AbstractModel):
    _name = 'report.bsd_dich_vu.bsd_bg_gt_view'

    @api.model
    def _get_report_values(self, docids, data=None):
        return {
            'doc_ids': data['ids'],
            'doc_model': data['model'],
            'docs': self.env['bsd.bg_gt'].browse(data['ids']),
        }