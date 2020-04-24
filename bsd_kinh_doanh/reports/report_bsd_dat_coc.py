# -*- coding:utf-8 -*-

from odoo import api, models, fields
import logging
import datetime
_logger = logging.getLogger(__name__)


class BsdWizardReportDatCoc(models.TransientModel):
    _name = 'bsd.dat_coc.report.wizard'
    _description = 'Chọn mẫu in Đặt cọc'

    def _get_dc(self):
        dc = self.env['bsd.dat_coc'].browse(self._context.get('active_ids', []))
        return dc

    bsd_dat_coc_id = fields.Many2one('bsd.dat_coc', string="Đặt cọc", default=_get_dc, readonly=True)
    bsd_mau_in = fields.Selection([('bsd_mau_in_dat_coc_chuan', 'Mẫu in chuẩn')], string="Mẫu in", required=True,
                                  default='bsd_mau_in_dat_coc_chuan')

    def action_in(self):
        """Call when button 'Get Report' clicked.
        """
        data = {
            'ids': self.bsd_dat_coc_id.ids,
            'model': self.bsd_dat_coc_id._name,
        }
        self.bsd_dat_coc_id.write({
            'bsd_ngay_in_dc': datetime.datetime.now(),
            'bsd_ngay_hh_kdc': datetime.datetime.now() + datetime.timedelta(days=self.bsd_dat_coc_id.bsd_du_an_id.bsd_hh_pc)
        })
        ref_id = 'bsd_kinh_doanh.' + self.bsd_mau_in
        return self.env.ref(ref_id).report_action(self, data=data)


class ReportBsdDatCoc(models.AbstractModel):
    _name = 'report.bsd_kinh_doanh.bsd_dat_coc_view'

    @api.model
    def _get_report_values(self, docids, data=None):
        return {
            'doc_ids': data['ids'],
            'doc_model': data['model'],
            'docs': self.env['bsd.dat_coc'].browse(data['ids']),
        }