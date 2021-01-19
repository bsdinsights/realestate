# -*- coding:utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError


class BsdLaiPhatTT(models.Model):
    _name = 'bsd.lai_phat_tt'
    _rec_name = 'bsd_ma_lptt'
    _description = "Cách tính lãi phạt chậm thanh toán"
    _inherit = ['mail.thread', 'mail.activity.mixin']

    bsd_ma_lptt = fields.Char(string="Mã", help="Mã lãi phạt chậm thanh toán", required=True, readonly=True, copy=False,
                              default='/')
    _sql_constraints = [
        ('bsd_ma_lptt_unique', 'unique (bsd_ma_lptt)',
         'Mã lãi phạt thanh toán đã tồn tại !'),
    ]
    bsd_ten_lptt = fields.Char(string="Tên", help="Tên lãi phạt thanh toán", required=True)
    bsd_dien_giai = fields.Char(string="Diễn giải", help="Diễn giải")
    bsd_du_an_id = fields.Many2one('bsd.du_an', string="Dự án", help="Tên dự án", required=True)
    bsd_tinh_phat = fields.Selection([('htt', 'Hạn thanh toán'), ('nah', "Ngày ân hạn")],
                                     string="PT tính phạt", default="htt",
                                     help="""
                                        Quy định tính lãi phạt chậm thanh toán từ ngày hết hạn thanh toán hay kể từ ngày ân hạn
                                     """, required=True)
    bsd_an_han = fields.Integer(string="Ân hạn", required=True,
                                help="""
                                    Số ngày ân hạn tính lãi phạt. Nếu khách hàng đóng tiền trong thời gian ân hạn, 
                                    sẽ không bị phạt thanh toán chậm    
                                """)
    bsd_lai_phat = fields.Float(string="Lãi phạt", help="Tỷ lệ đóng lãi phạt theo năm")
    bsd_so_ngay_nam = fields.Integer(string="Số ngày trong năm",
                                     help="Số ngày dùng để tính phần trăm chiết khấu thanh toán trước hạn", default=365)
    bsd_tien_td = fields.Monetary(string="Tiền phạt tối đa", help="Tiền phạt chậm thanh toán tối đa")
    bsd_tl_td = fields.Float(string="Tỷ lệ phạt tối đa", help="Tỷ lệ tối đa phạt chậm thanh toán")
    state = fields.Selection([('active', 'Áp dụng'),
                              ('inactive', 'Ngưng áp dụng')],
                             string="Trạng thái", default='active', required=True, tracking=1, help="Trạng thái")
    company_id = fields.Many2one('res.company', string='Công ty', default=lambda self: self.env.company)
    currency_id = fields.Many2one(related="company_id.currency_id", string="Tiền tệ", readonly=True)

    def name_get(self):
        res = []
        for lt in self:
            res.append((lt.id, lt.bsd_ten_lptt))
        return res

    @api.model
    def create(self, vals):
        sequence = False
        if 'bsd_du_an_id' in vals:
            du_an = self.env['bsd.du_an'].browse(vals['bsd_du_an_id'])
            sequence = du_an.get_ma_bo_cn(loai_cn=self._name)
        if not sequence:
            raise UserError(_('Dự án chưa có mã lãi phạt chậm thanh toán.'))
        vals['bsd_ma_lptt'] = sequence.next_by_id()
        return super(BsdLaiPhatTT, self).create(vals)