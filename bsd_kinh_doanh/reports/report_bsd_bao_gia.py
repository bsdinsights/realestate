# -*- coding:utf-8 -*-

from odoo import api, models, fields
import logging
import datetime
_logger = logging.getLogger(__name__)


class BsdWizardReportBaoGia(models.TransientModel):
    _name = 'bsd.bao_gia.report.wizard'
    _description = 'Chọn mẫu in báo giá'

    def _get_bg(self):
        bg = self.env['bsd.bao_gia'].browse(self._context.get('active_ids', []))
        return bg

    bsd_bao_gia_id = fields.Many2one('bsd.bao_gia', string="Báo giá", default=_get_bg, readonly=True)
    bsd_mau_in = fields.Selection([('bsd_mau_in_bao_gia_chuan', 'Mẫu in chuẩn')], string="Mẫu in", required=True,
                                  default='bsd_mau_in_bao_gia_chuan')

    def action_in(self):
        """Call when button 'Get Report' clicked.
        """
        data = {
            'ids': self.bsd_bao_gia_id.ids,
            'model': self.bsd_bao_gia_id._name,
        }
        self.bsd_bao_gia_id.write({
            'bsd_ngay_in_bg': datetime.datetime.now(),
            'bsd_ngay_hh_kbg': datetime.datetime.now() + datetime.timedelta(days=self.bsd_bao_gia_id.bsd_du_an_id.bsd_hh_bg)
        })
        ref_id = 'bsd_kinh_doanh.' + self.bsd_mau_in
        return self.env.ref(ref_id).report_action(self, data=data)


class ReportBsdBaoGia(models.AbstractModel):
    _name = 'report.bsd_kinh_doanh.bsd_bao_gia_view'

    @api.model
    def _get_report_values(self, docids, data=None):
        return {
            'doc_ids': data['ids'],
            'doc_model': data['model'],
            'docs': self.env['bsd.bao_gia'].browse(data['ids']),
        }