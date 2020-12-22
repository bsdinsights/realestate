# -*- coding:utf-8 -*-

from odoo import api, models, fields
from odoo.exceptions import UserError
import logging
import datetime
from dateutil import tz
_logger = logging.getLogger(__name__)


class BsdWizardReportThongBaoKQDD(models.TransientModel):
    _name = 'bsd.tb_kq_dttt.report.wizard'
    _description = 'Chọn mẫu in thông báo kết quả đo đạt'

    def _get_tb_tt(self):
        tb_tt = self.env['bsd.tb_kq_dttt'].browse(self._context.get('active_ids', []))
        return tb_tt

    bsd_tb_kq_dttt_id = fields.Many2one('bsd.tb_kq_dttt', string="Thông báo", default=_get_tb_tt, readonly=True)
    bsd_mau_in = fields.Selection([('bsd_mau_in_bsd_tb_kq_dttt_html', 'Thông báo kết quả đo đạt(html)'),
                                   ('bsd_mau_in_bsd_tb_kq_dttt', 'Thông báo kết quả đo đạt')],
                                  string="Mẫu in", required=True,
                                  default='bsd_mau_in_bsd_tb_kq_dttt_html')

    def action_in(self):
        data = {
            'ids': self.bsd_tb_kq_dttt_id.ids,
            'model': self.bsd_tb_kq_dttt_id._name,
        }
        self.bsd_tb_kq_dttt_id.write({
            'bsd_ngay_in': datetime.date.today(),
            'bsd_nguoi_in_id': self.env.uid
        })
        ref_id = 'bsd_dich_vu.' + self.bsd_mau_in
        return self.env.ref(ref_id).report_action(self, data=data)


class ReportBsdKQDTTT(models.AbstractModel):
    _name = 'report.bsd_dich_vu.bsd_tb_kq_dttt_view'

    @api.model
    def _get_report_values(self, docids, data=None):
        doc = self.env['bsd.tb_kq_dttt'].browse(data['ids'])
        return {
            'doc_ids': data['ids'],
            'doc_model': data['model'],
            'docs': doc,
        }
