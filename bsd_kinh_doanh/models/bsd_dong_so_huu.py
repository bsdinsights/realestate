# -*- coding:utf-8 -*-
from odoo import models, fields


class BsdDongSoHuu(models.Model):
    _name = 'bsd.dong_so_huu'
    _description = 'Người đồng sở hữu'
    _rec_name = 'bsd_dong_sh_id'

    bsd_dong_sh_id = fields.Many2one('res.partner', string="Đồng sở hữu", help="Người đồng sở hữu", required=True)
    mobile = fields.Char(related='bsd_dong_sh_id.mobile', string="Di động")
    email = fields.Char(related='bsd_dong_sh_id.email', string="Email")
    bsd_ma_kh = fields.Char(related='bsd_dong_sh_id.bsd_ma_kh', string="Mã khách hàng")
    bsd_quan_he = fields.Selection([('vo', 'Vợ'),
                                    ('chong', 'Chồng'),
                                    ('con', 'Con'),
                                    ('chau', 'Cháu'),
                                    ('nguoi_than', 'Người thân'),
                                    ('ban', 'Bạn'),
                                    ('khac', 'Khác')
                                    ], string="Mối quan hệ", required=True)
    bsd_bao_gia_id = fields.Many2one('bsd.bao_gia', string="Bảng tính giá", readonly=True)
    bsd_dat_coc_id = fields.Many2one('bsd.dat_coc', string="Đặt cọc", readonly=True)
    bsd_chuyen_dd_id = fields.Many2one('bsd.dat_coc.chuyen_dd', string="Thay đổi người ký TTĐC/HĐMB")
