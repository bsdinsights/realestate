# -*- coding:utf-8 -*-

from odoo import models, fields, api


class BsdTknhAp(models.Model):
    _name = 'bsd.tknh_ad'
    _description = 'Tài khoản ngân hàng đang áp dụng'
    _rec_name = 'bsd_ten_tknh'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    bsd_ma_tknh = fields.Char(string="Mã", required=True)
    _sql_constraints = [
        ('bsd_ma_tknh_unique', 'unique (bsd_ma_tknh)',
         'Mã tài khoản ngân hàng đang áp dụng đã tồn tại !'),
    ]
    bsd_ten_tknh = fields.Char(string="Tên", required=True)
    bsd_du_an_id = fields.Many2one('bsd.du_an', string="Dự án", required=True)
    bsd_da_tknh_id = fields.Many2one('res.partner.bank', string="Tài khoản ngân hàng", required=True)
    bsd_tu_ngay = fields.Date(string="Từ ngày", help="Ngày bắt đầu áp dụng tài khoản ngân hàng", required=True)
    bsd_den_ngay = fields.Date(string="Đến ngày", help="Ngày kết thúc áp dụng tài khoản ngân hàng", required=True)
    bsd_dien_giai = fields.Char(string="Diễn giải")
    state = fields.Selection([('active', 'Đang sử dụng'),
                              ('inactive', 'Không sử dụng')],
                             string="Trạng thái", default='active', required=True, help="Trạng thái", tracking=1)
    bsd_tknh_ch_ids = fields.One2many('bsd.tknh_ch', 'bsd_ma_tkad_id', string="Chi tiết")

    @api.onchange('bsd_du_an_id')
    def _onchange_bsd_du_an_id(self):
        rec = {}
        id_tknh = self.bsd_du_an_id.bsd_tk_ng_ids.mapped('bsd_tk_nh_id').ids or []
        rec.update({
            'domain': {'bsd_da_tknh_id': [('id', 'in', id_tknh)]}
        })
        return rec



class BsdTknhCh(models.Model):
    _name = 'bsd.tknh_ch'
    _description = "Tài khoản ngân hàng đang áp dụng căn hộ"
    _rec_name = 'bsd_can_ho_id'

    bsd_du_an_id = fields.Many2one('bsd.du_an', string="Dự án", required=True)
    bsd_can_ho_id = fields.Many2one('product.product', string="Căn hộ", required=True)
    bsd_so_tk = fields.Char(string="Số tài khoản", required=True)
    bsd_ma_tkad_id = fields.Many2one('bsd.tknh_ad', string="Tài khoản ngân hàng áp dụng", required=True)
    state = fields.Selection([('active', 'Đang sử dụng'),
                              ('inactive', 'Không sử dụng')],
                             string="Trạng thái", default='active', required=True)



