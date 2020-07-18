# -*- coding:utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError


class BsdDanhSachThongBao(models.Model):
    _name = 'bsd.ds_tb'
    _description = "Danh sách thông báo"
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _rec_name = 'bsd_ma_ds_tb'

    bsd_ma_ds_tb = fields.Char(string="Mã", help="Mã danh sách thông báo", required=True, readonly=True,
                               copy=False, default='/')
    _sql_constraints = [
        ('bsd_ma_ds_tb_unique', 'unique (bsd_ma_ds_tb)',
         'Mã danh sách thông báo đã tồn tại !')
    ]
    bsd_ngay_ds_tb = fields.Datetime(string="Ngày tạo", required=True, default=lambda self: fields.Datetime.now(),
                                     readonly=True,
                                     states={'nhap': [('readonly', False)]})
    bsd_du_an_id = fields.Many2one('bsd.du_an', string="Dự án", required=True,
                                   readonly=True,
                                   states={'nhap': [('readonly', False)]})
    bsd_loai = fields.Selection([('nt', 'Nghiệm thu'), ('bg', 'Bàn giao')], string="Loại thông báo",
                                required=True, default='nhap')
    bsd_cn_dkbg_ids = fields.Many2many('bsd.cn_dkbg', string="Danh sách cập nhật DKBG",
                                       readonly=True,
                                       states={'nhap': [('readonly', False)]})
    state = fields.Selection([('nhap', 'Nháp'), ('xac_nhan', 'Xác nhận')],
                             string="Trạng thái", default="nhap", required=True, readonly=True, tracking=1)

    @api.model
    def create(self, vals):
        sequence = False
        if 'bsd_du_an_id' in vals:
            du_an = self.env['bsd.du_an'].browse(vals['bsd_du_an_id'])
            sequence = du_an.get_ma_bo_cn(loai_cn=self._name)
        if not sequence:
            raise UserError(_('Dự án chưa có mã danh sách thông báo'))
        vals['bsd_ma_cn'] = sequence.next_by_id()
        return super(BsdDanhSachThongBao, self).create(vals)