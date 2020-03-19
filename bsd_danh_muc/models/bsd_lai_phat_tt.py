# -*- coding:utf-8 -*-

from odoo import models, fields, api


class BsdLaiPhatTT(models.Model):
    _name = 'bsd.lai_phat_tt'
    _rec_name = 'bsd_ten_lptt'
    _description = "Thông tin lãi phạt thanh toán"
    _inherit = ['mail.thread', 'mail.activity.mixin']

    bsd_ma_lptt = fields.Char(string="Mã", help="Mã lãi phạt thanh toán", required=True)
    bsd_ten_lptt = fields.Char(string="Tên", help="Tên lãi phạt thanh toán", required=True)
    bsd_dien_giai = fields.Char(string="Diễn giải")
    bsd_du_an_id = fields.Many2one('bsd.du_an', string="Dự án")
    bsd_tinh_phat = fields.Selection([('htt', 'Hạn thanh toán'), ('nah', "Ngày ân hạn")],
                                     string="Tính phạt", default="htt",
                                     help="""
                                        Quy định tính lại phạt từ ngày hết hạn thanh toán hay kể từ ngày ân hạn
                                     """)
    bsd_an_han = fields.Integer(string="Ân hạn", required=True,
                                help="""
                                    Số ngày ân hạn tính lãi phạt. Nếu khách hàng đóng tiền trong thời gian ân hạn, 
                                    sẽ không bị phạt thanh toán chậm    
                                """)
    bsd_lai_phat = fields.Float(string="Lãi phạt (%/ngày)", help="Tỷ lệ đóng lãi phạt theo ngày")
    bsd_tien_td = fields.Monetary(string="Tiền phạt tối đa", help="Tiền phạt chậm thanh toán tối đa")
    bsd_tl_td = fields.Float(string="Tỷ lệ phạt tối đa", help="Tỷ lệ tối đa phạt chậm thanh toán")
    state = fields.Selection([('active', 'Đang sử dụng'),
                              ('inactive', 'Ngưng sử dụng')],
                             string="Trạng thái", default='active', required=True)
    company_id = fields.Many2one('res.company', string='Công ty', default=lambda self: self.env.company)
    currency_id = fields.Many2one(related="company_id.currency_id", string="Tiền tệ", readonly=True)