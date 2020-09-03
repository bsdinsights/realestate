# -*- coding:utf-8 -*-

from odoo import models, fields, api
from odoo.exceptions import ValidationError


class BsdThueSuat(models.Model):
    _name = 'bsd.thue_suat'
    _description = "Bảng thông tin thuế suất"
    _rec_name = 'bsd_ten_ts'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    bsd_ma_ts = fields.Char(string="Mã", help="Mã", required=True)
    _sql_constraints = [
        ('bsd_ma_ts_unique', 'unique (bsd_ma_ts)',
         'Mã thuế suất đã tồn tại !'),
    ]
    bsd_ten_ts = fields.Char(string="Tên", help="Tên", required=True)
    bsd_thue_suat = fields.Float(string="Thuế suất", required=True, help="Thuế suất áp dụng")
    bsd_dien_giai = fields.Char(string="Diễn giải", help="Diễn giải")
    state = fields.Selection([('active', 'Đang sử dụng'),
                              ('inactive', 'Không sử dụng')],
                             string="Trạng thái", default='active', required=True, tracking=1, help="Trạng thái")

    @api.constrains('bsd_thue_suat')
    def _check_bsd_thue_suat(self):
        for record in self:
            if record.bsd_thue_suat > 100 or record.bsd_thue_suat < 0:
                raise ValidationError("Thuế suất nằm trong khoảng 0 đến 100")