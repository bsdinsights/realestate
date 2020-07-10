# -*- coding:utf-8 -*-

from odoo import api, models, fields
import logging
import datetime
_logger = logging.getLogger(__name__)


class BsdWizardReportHopDong(models.TransientModel):
    _name = 'bsd.hd_ban.report.wizard'
    _description = 'Chọn mẫu in hợp đồng'

    def _get_hdb(self):
        hdb = self.env['bsd.hd_ban'].browse(self._context.get('active_ids', []))
        return hdb

    bsd_hd_ban_id = fields.Many2one('bsd.hd_ban', string="Hợp đồng bán", default=_get_hdb, readonly=True)
    bsd_mau_in = fields.Selection([('bsd_mau_in_hdb', 'Hợp đồng (html)'),
                                   ('bsd_mau_in_ttdc', 'Thỏa thuận đặt cọc (html)')], string="Mẫu in", required=True,
                                  default='bsd_mau_in_hdb')

    def action_in(self):
        """Call when button 'Get Report' clicked.
        """
        data = {
            'ids': self.bsd_hd_ban_id.ids,
            'model': self.bsd_hd_ban_id._name,
        }
        if self.bsd_mau_in == 'bsd_mau_in_hdb':
            if not self.bsd_hd_ban_id.bsd_ngay_in_hdb:
                self.bsd_hd_ban_id.write({
                    'bsd_ngay_in_hdb': datetime.datetime.now(),
                    'bsd_ngay_hh_khdb': datetime.datetime.now() + datetime.timedelta(days=self.bsd_du_an_id.bsd_hh_hd)
                })
        if self.bsd_mau_in == 'bsd_mau_in_ttdc':
            if not self.bsd_hd_ban_id.bsd_ngay_in_ttdc:
                self.bsd_hd_ban_id.write({
                    'bsd_ngay_in_ttdc': datetime.datetime.now(),
                })
        ref_id = 'bsd_dich_vu.' + self.bsd_mau_in

        _logger.debug(ref_id)
        return self.env.ref(ref_id).report_action(self, data=data)


class ReportBsdHdBan(models.AbstractModel):
    _name = 'report.bsd_dich_vu.bsd_hd_ban_view'

    @api.model
    def _get_report_values(self, docids, data=None):
        _logger.debug("Chạy tới đây")
        return {
            'doc_ids': data['ids'],
            'doc_model': data['model'],
            'docs': self.env['bsd.hd_ban'].browse(data['ids']),
        }


class ReportBsdTTDC(models.AbstractModel):
    _name = 'report.bsd_dich_vu.bsd_ttdc_view'

    @api.model
    def _get_report_values(self, docids, data=None):
        _logger.debug("Chạy tới đây")
        return {
            'doc_ids': data['ids'],
            'doc_model': data['model'],
            'docs': self.env['bsd.hd_ban'].browse(data['ids']),
        }

