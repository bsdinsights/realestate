# -*- coding:utf-8 -*-

from odoo import api, models
import logging
_logger = logging.getLogger(__name__)


class ReportBsdBaoGia(models.AbstractModel):
    _name = 'report.bsd_kinh_doanh.bsd_bao_gia_view'

    @api.model
    def _get_report_values(self, docids, data=None):
        return {
            'doc_ids': docids,
            'doc_model': 'bsd.bao_gia',
            'docs': self.env['bsd.bao_gia'].browse(docids),
            'report_type': data.get('report_type') if data else '',
        }