# -*- coding:utf-8 -*-

from odoo import api, models, fields
import logging
import datetime
from dateutil import tz
_logger = logging.getLogger(__name__)


class BsdWizardReportTBNT(models.TransientModel):
    _name = 'bsd.tb_bg.report.wizard'
    _description = 'Chọn mẫu in thông báo bàn giao'

    def _get_tbnt(self):
        nt = self.env['bsd.tb_bg'].browse(self._context.get('active_ids', []))
        return nt

    bsd_tb_bg_id = fields.Many2one('bsd.tb_bg', string="Thông báo bàn giao", default=_get_tbnt, readonly=True)
    bsd_mau_in = fields.Selection([('bsd_mau_in_tb_bg_html', 'Thông báo bàn giao (html)'),
                                   ('bsd_mau_in_tb_bg', 'Thông báo bàn giao')], string="Mẫu in", required=True,
                                  default='bsd_mau_in_tb_bg_html')

    def action_in(self):
        """Call when button 'Get Report' clicked.
        """
        data = {
            'ids': self.bsd_tb_bg_id.ids,
            'model': self.bsd_tb_bg_id._name,
        }
        self.bsd_tb_bg_id.write({
            'bsd_ngay_in': datetime.datetime.now(),
        })
        ref_id = 'bsd_dich_vu.' + self.bsd_mau_in
        return self.env.ref(ref_id).report_action(self, data=data)


class ReportBsdTBNT(models.AbstractModel):
    _name = 'report.bsd_dich_vu.bsd_tb_bg_view'

    @api.model
    def _get_report_values(self, docids, data=None):
        _logger.debug("Chạy tới đây")
        ngay_ht = datetime.datetime.now()
        from_zone = tz.gettz('UTC')
        to_zone = tz.gettz(self._context['tz'])
        ngay_ht = ngay_ht.replace(tzinfo=from_zone)
        ngay_ht = ngay_ht.astimezone(to_zone)
        return {
            'doc_ids': data['ids'],
            'doc_model': data['model'],
            'docs': self.env['bsd.tb_nt'].browse(data['ids']),
            'ngay_ht': ngay_ht,
        }