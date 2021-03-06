# -*- coding:utf-8 -*-

from odoo import models, fields, api, _


class BsdDuAn(models.Model):
    _inherit = 'bsd.du_an'

    bsd_ma_bo_cn_ids = fields.One2many('bsd.ma_bo_cn', 'bsd_du_an_id', string="Mã bộ chứng từ",
                                       readonly=True,
                                       states={'chuan_bi': [('readonly', False)]})

    def get_ma_bo_cn(self, loai_cn):
        if self.bsd_ma_bo_cn_ids:
            ma_cn = self.bsd_ma_bo_cn_ids.filtered(lambda m: m.bsd_loai_cn == loai_cn and m.state == 'active')
            if ma_cn:
                return ma_cn[0].bsd_ma_tt_id
            else:
                return False
        else:
            return False
