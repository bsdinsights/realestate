# -*- coding:utf-8 -*-

from odoo import api, models, fields
import logging
import datetime
_logger = logging.getLogger(__name__)


class BsdWizardReportChuyenNhuongHopDong(models.TransientModel):
    _name = 'bsd.hd_ban_cn.report.wizard'
    _description = 'Chọn mẫu in chuyển nhượng'

    def _get_hdb_cn(self):
        hdb = self.env['bsd.hd_ban_cn'].browse(self._context.get('active_ids', []))
        return hdb

    bsd_hd_ban_cn_id = fields.Many2one('bsd.hd_ban_cn', string="Chuyển nhượng HĐMB", default=_get_hdb_cn,
                                       readonly=True)
    bsd_mau_in = fields.Selection([('bsd_mau_in_vbcn', 'Văn bản chuyển nhượng'),
                                   ('bsd_mau_in_xncn', 'Xác nhận cho phép chuyển nhượng')], string="Mẫu in",
                                  required=True,
                                  default='bsd_mau_in_vbcn')

    def action_in(self):
        """Call when button 'Get Report' clicked.
        """
        data = {
            'ids': self.bsd_hd_ban_cn_id.ids,
            'model': self.bsd_hd_ban_cn_id._name,
        }
        if not self.bsd_hd_ban_cn_id.bsd_ngay_in_vb:
            self.bsd_hd_ban_cn_id.write({
                'bsd_ngay_in_vb': datetime.datetime.now(),
            })
        ref_id = 'bsd_dich_vu.' + self.bsd_mau_in

        _logger.debug(ref_id)
        return self.env.ref(ref_id).report_action(self, data=data)


class ReportBsdVBCN(models.AbstractModel):
    _name = 'report.bsd_dich_vu.bsd_vb_cn_view'

    @api.model
    def _get_report_values(self, docids, data=None):
        return {
            'doc_ids': data['ids'],
            'doc_model': data['model'],
            'docs': self.env['bsd.hd_ban_cn'].browse(data['ids']),
        }


class ReportBsdXacNhanCn(models.AbstractModel):
    _name = 'report.bsd_dich_vu.bsd_xn_cn_view'

    @api.model
    def _get_report_values(self, docids, data=None):
        return {
            'doc_ids': data['ids'],
            'doc_model': data['model'],
            'docs': self.env['bsd.hd_ban_cn'].browse(data['ids']),
        }