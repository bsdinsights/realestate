# -*- coding:utf-8 -*-

from odoo import api, models, fields
import logging
import datetime
from dateutil import tz
_logger = logging.getLogger(__name__)


class BsdWizardReportThanhLy(models.TransientModel):
    _name = 'bsd.tb_tt_nn.report.wizard'
    _description = 'Chọn mẫu in thông báo thanh toán nhắc nợ'

    def _get_tb_tt_nn(self):
        tb_tt_nn = self.env['bsd.tb_tt_nn'].browse(self._context.get('active_ids', []))
        return tb_tt_nn

    bsd_tb_tt_nn_id = fields.Many2one('bsd.tb_tt_nn', string="Thông báo", default=_get_tb_tt_nn, readonly=True)
    bsd_mau_in = fields.Selection([('bsd_mau_in_tb_tt_nn_html', 'Thông báo thanh toán (html)'),
                                   ('bsd_mau_in_tb_tt_nn', 'Thông báo thanh toán')], string="Mẫu in", required=True,
                                  default='bsd_mau_in_tb_tt_nn_html')

    def action_in(self):
        """Call when button 'Get Report' clicked.
        """
        data = {
            'ids': self.bsd_tb_tt_nn_id.ids,
            'model': self.bsd_tb_tt_nn_id._name,
        }
        self.bsd_tb_tt_nn_id.write({
            'bsd_ngay_in': datetime.datetime.now(),
        })
        ref_id = 'bsd_dich_vu.' + self.bsd_mau_in
        return self.env.ref(ref_id).report_action(self, data=data)


class ReportBsdTBTL(models.AbstractModel):
    _name = 'report.bsd_dich_vu.bsd_tb_tt_nn_view'

    @api.model
    def _get_report_values(self, docids, data=None):
        doc = self.env['bsd.tb_tt_nn'].browse(data['ids'])
        ngay_ht = datetime.datetime.now()
        from_zone = tz.gettz('UTC')
        to_zone = tz.gettz(self._context['tz'])
        ngay_ht = ngay_ht.replace(tzinfo=from_zone)
        ngay_ht = ngay_ht.astimezone(to_zone)
        return {
            'doc_ids': data['ids'],
            'doc_model': data['model'],
            'docs': doc,
            'ngay_ht': ngay_ht,
        }