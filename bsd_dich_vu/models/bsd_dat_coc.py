# -*- coding:utf-8 -*-

from odoo import models, fields, api
from odoo.exceptions import UserError
import datetime
import logging
_logger = logging.getLogger(__name__)


class BsdDatCoc(models.Model):
    _inherit = 'bsd.dat_coc'

    def auto_tao_ds_td(self):
        self.env['bsd.ds_td'].create({
            'bsd_loai_td': 'vp_tg',
            'bsd_loai_yc': 'gia_han',
            'bsd_loai_dt': 'dat_coc',
            'bsd_du_an_id': self.bsd_du_an_id.id,
            'bsd_unit_id': self.bsd_unit_id.id,
            'bsd_khach_hang_id': self.bsd_khach_hang_id.id,
            'bsd_tien_dc': self.bsd_tien_dc,
            'bsd_ngay_hh': self.bsd_ngay_hh_kdc,
            'bsd_tien_da_tt': self.bsd_tien_da_tt,
        })