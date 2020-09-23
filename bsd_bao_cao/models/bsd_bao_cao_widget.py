# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from odoo.exceptions import UserError
import logging
_logger = logging.getLogger(__name__)


class BsdBaoCaoWidget(models.AbstractModel):
    _name = 'bsd.bao_cao.widget'
    _description = 'Báo cáo'

    bsd_du_an_id = fields.Many2one('bsd.du_an', string="Dự án", help="Dự án")
    bsd_tu_ngay = fields.Date(string="Từ ngày")
    bsd_den_ngay = fields.Date(string="Đến ngày")

    @api.model
    def action_search(self, data):
        if not data['bsd_du_an_id']:
            raise UserError("Vui lòng điền trường dự án")
        if not data['bsd_loai']:
            raise UserError("Vui lòng chọn loại báo cáo")
        _logger.debug("Dữ liệu")
        _logger.debug(data)