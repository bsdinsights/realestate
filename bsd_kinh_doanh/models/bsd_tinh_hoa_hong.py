# -*- coding:utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError
import logging
_logger = logging.getLogger(__name__)


class BsdTinhHoaHong(models.Model):
    _name = 'bsd.tinh_hoa_hong'
    _rec_name = 'bsd_ten'
    _description = "Tính hoa hồng cho nhân viên nội bộ"
    _inherit = ['mail.thread', 'mail.activity.mixin']

    bsd_ma = fields.Char(string="Mã", help="Mã tính hoa hồng cho nhân viên nội bộ", required=True, readonly=True, copy=False,
                         default='/')
    _sql_constraints = [
        ('bsd_ma_unique', 'unique (bsd_ma)',
         'Mã tính hoa hồng đã tồn tại !'),
    ]
    bsd_ten = fields.Char(string="Tiêu đề", required=True, help="Tên tính hoa hồng",
                          readonly=True,
                          states={'nhap': [('readonly', False)]})
    bsd_du_an_id = fields.Many2one('bsd.du_an', string="Dự án", help="Tên dự án", required=True,
                                   readonly=True,
                                   states={'nhap': [('readonly', False)]})
    bsd_toa_nha_id = fields.Many2one('bsd.toa_nha', string="Tòa nhà/ khu", required=True, help="Tên tòa nhà hoặc khu",
                                     readonly=True,
                                     states={'nhap': [('readonly', False)]})
    bsd_tang_id = fields.Many2one('bsd.tang', string="Tầng/ dãy", required=True, help="Tên tầng lầu hoặc dãy nhà",
                                  readonly=True,
                                  states={'nhap': [('readonly', False)]})
    bsd_cach_tinh = fields.Selection([('ko_ht', 'Không hồi tố'), ('hoi_to', 'Hồi tố')], string="Cách tính",
                                     readonly=True, states={'nhap': [('readonly', False)]}, required=True)
    bsd_tu_ngay = fields.Date(string="Từ ngày", help="Ngày bắt đầu chốt hoa hồng ",
                              readonly=True, required=True,
                              states={'nhap': [('readonly', False)]})
    bsd_den_ngay = fields.Date(string="Đến ngày", help="Ngày kết thúc chốt hoa hồng",
                               readonly=True, required=True,
                               states={'nhap': [('readonly', False)]})
    state = fields.Selection([('nhap', 'Nháp'),
                              ('da_tinh', 'Đã tính'),
                              ('xac_nhan', 'Xác nhận'),
                              ('chua_chi', 'Chưa chi'),
                              ('da_chi', 'Đã chi'),
                              ('huy', 'Hủy')], string="Trạng thái", help="Trạng thái",
                             required=True, default='nhap', tracking=1)

    @api.model
    def create(self, vals):
        sequence = False
        if 'bsd_du_an_id' in vals:
            du_an = self.env['bsd.du_an'].browse(vals['bsd_du_an_id'])
            sequence = du_an.get_ma_bo_cn(loai_cn=self._name)
        if not sequence:
            raise UserError(_('Dự án chưa có mã tính hoa hồng.'))
        vals['bsd_ma'] = sequence.next_by_id()
        return super(BsdTinhHoaHong, self).create(vals)
