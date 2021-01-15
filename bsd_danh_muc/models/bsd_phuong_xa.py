# -*- coding:utf-8 -*-

from odoo import models, fields, api


class BsdPhuongXa(models.Model):
    _name = 'bsd.phuong_xa'
    _rec_name = 'bsd_ten'
    _description = 'Danh mục phường xã'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    bsd_quoc_gia_id = fields.Many2one('res.country', string="Quốc gia", required=True)
    bsd_tinh_thanh_id = fields.Many2one('res.country.state', string="Tỉnh thành",
                                        required=True)
    bsd_quan_huyen_id = fields.Many2one('bsd.quan_huyen', string="Quận huyện", required=True)
    bsd_ten = fields.Char(string="Tên phường xã", required=True)
    bsd_ma = fields.Char(string="Mã phường xã", required=True)
    _sql_constraints = [
        ('bsd_ma_unique', 'unique (bsd_ma)',
         'Mã phường xã đã tồn tại !'),
    ]
    bsd_dien_giai = fields.Char(string="Diễn giải")
    state = fields.Selection([('active', "Đang sử dụng"),
                              ('inactive', "Không sử dụng")], string='Trạng thái',
                             default='active', tracking=1, help="Trạng thái")

    @api.model
    def _name_search(self, name='', args=None, operator='ilike', limit=100, name_get_uid=None):
        args = list(args or [])
        if name:
            if operator == 'ilike':
                args += [('bsd_ten', operator, name)]
            elif operator == '=':
                args += [('bsd_ma', operator, name)]
        access_rights_uid = name_get_uid or self._uid
        ids = self._search(args, limit=limit, access_rights_uid=access_rights_uid)
        recs = self.browse(ids)
        return models.lazy_name_get(recs.with_user(access_rights_uid))
