# -*- coding:utf-8 -*-

from odoo import api, models, fields
import logging
import datetime
_logger = logging.getLogger(__name__)


class BsdWizardReportViPhamHopDong(models.TransientModel):
    _name = 'bsd.vp_hd.report.wizard'
    _description = 'Chọn mẫu in vi phạm hợp đồng'

    def _get_vp_hd(self):
        hdb = self.env['bsd.vp_hd'].browse(self._context.get('active_ids', []))
        return hdb

    bsd_vp_hd_id = fields.Many2one('bsd.vp_hd', string="Vi phạm HĐ", default=_get_vp_hd,
                                   readonly=True)
    bsd_mau_in = fields.Selection([('bsd_mau_in_vphd', 'Biên bản vi phạm hợp đồng')], string="Mẫu in",
                                  required=True,
                                  default='bsd_mau_in_vphd')

    def action_in(self):
        """Call when button 'Get Report' clicked.
        """
        data = {
            'ids': self.bsd_vp_hd_id.ids,
            'model': self.bsd_vp_hd_id._name,
        }
        if not self.bsd_vp_hd_id.bsd_ngay_in:
            self.bsd_vp_hd_id.write({
                'bsd_ngay_in': datetime.date.today(),
                'bsd_nguoi_in_id': self.env.uid,
            })
        ref_id = 'bsd_dich_vu.' + self.bsd_mau_in

        _logger.debug(ref_id)
        return self.env.ref(ref_id).report_action(self, data=data)


class ReportBsdVBCN(models.AbstractModel):
    _name = 'report.bsd_dich_vu.bsd_vp_hd_view'

    @api.model
    def _get_report_values(self, docids, data=None):
        return {
            'doc_ids': data['ids'],
            'doc_model': data['model'],
            'docs': self.env['bsd.vp_hd'].browse(data['ids']),
        }