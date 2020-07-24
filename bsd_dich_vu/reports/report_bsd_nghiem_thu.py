# -*- coding:utf-8 -*-

from odoo import api, models, fields
import logging
import datetime
_logger = logging.getLogger(__name__)


class BsdWizardReportNghiemThu(models.TransientModel):
    _name = 'bsd.nghiem_thu.report.wizard'
    _description = 'Chọn mẫu in nghiệm thu sản phẩm'

    def _get_nghiem_thu(self):
        nt = self.env['bsd.nghiem_thu'].browse(self._context.get('active_ids', []))
        return nt

    bsd_nghiem_thu_id = fields.Many2one('bsd.nghiem_thu', string="Nghiệm thu", default=_get_nghiem_thu, readonly=True)
    bsd_mau_in = fields.Selection([('bsd_mau_in_nghiem_thu_html', 'Nghiệm thu sản phẩm(html)'),
                                   ('bsd_mau_in_nghiem_thu', 'Nghiệm thu sản phẩm')], string="Mẫu in", required=True,
                                  default='bsd_mau_in_nghiem_thu_html')

    def action_in(self):
        """Call when button 'Get Report' clicked.
        """
        data = {
            'ids': self.bsd_nghiem_thu_id.ids,
            'model': self.bsd_nghiem_thu_id._name,
        }
        if not self.bsd_nghiem_thu_id.bsd_ngay_in_bb:
            self.bsd_nghiem_thu_id.write({
                'bsd_ngay_in_bb': fields.Datetime.now(),
            })
        ref_id = 'bsd_dich_vu.' + self.bsd_mau_in
        return self.env.ref(ref_id).report_action(self, data=data)


class ReportBsdNghiemThu(models.AbstractModel):
    _name = 'report.bsd_dich_vu.bsd_nghiem_thu_view'

    @api.model
    def _get_report_values(self, docids, data=None):
        _logger.debug("Chạy tới đây")
        return {
            'doc_ids': data['ids'],
            'doc_model': data['model'],
            'docs': self.env['bsd.nghiem_thu'].browse(data['ids']),
        }