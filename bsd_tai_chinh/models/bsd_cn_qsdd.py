# -*- coding:utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError


class BsdCapNhatGTQSDD(models.Model):
    _name = 'bsd.cn_qsdd'
    _description = "Cập nhật giá trị QSDĐ"
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _rec_name = 'bsd_ten'

    bsd_ma = fields.Char(string="Mã", help="Mã danh sách cập nhật giá trị QSDĐ", required=True, readonly=True,
                                 copy=False, default='/')
    _sql_constraints = [
        ('bsd_ma_unique', 'unique (bsd_ma)',
         'Mã cập nhật giá trị QSDĐ đã tồn tại !')
    ]
    bsd_ten = fields.Char(string="Tiêu đề", help="Tiêu đề", required=True,
                          readonly=True,
                          states={'nhap': [('readonly', False)]})
    bsd_ngay = fields.Date(string="Ngày tạo", required=True, default=lambda self: fields.Date.today(),
                           readonly=True,
                           states={'nhap': [('readonly', False)]})
    bsd_du_an_id = fields.Many2one('bsd.du_an', string="Dự án", help="Dự án", required=True,
                                   readonly=True,
                                   states={'nhap': [('readonly', False)]})
    bsd_dien_giai = fields.Char(string="Diễn giải", help="Diễn giải",
                                readonly=True,
                                states={'nhap': [('readonly', False)]})
    bsd_ngay_duyet = fields.Datetime(string="Ngày duyệt", readonly=True, help="Ngày duyệt")
    bsd_nguoi_duyet_id = fields.Many2one('res.users', string="Người duyệt", help="Người duyệt", readonly=True)

    state = fields.Selection([('nhap', 'Nháp'), ('xac_nhan', 'Xác nhận'),
                              ('duyet', 'Duyệt'), ('huy', 'Hủy')],
                             string="Trạng thái", default="nhap", required=True, readonly=True, tracking=1)
    bsd_ly_do = fields.Char(string="Lý do", readonly=True, tracking=2)
    bsd_ct_ids = fields.One2many('bsd.cn_qsdd_unit', 'bsd_cn_qsdd_id', string="Cập nhật QSDĐ chi tiết")

    # tính năng import dự liệu
    def action_nhap_sp(self):
        action = {
            'type': 'ir.actions.client',
            'tag': 'import',
            'params': {
                'model': 'bsd.cn_qsdd_unit'
            }
        }
        return action

    @api.model
    def create(self, vals):
        sequence = None
        if 'bsd_du_an_id' in vals:
            du_an = self.env['bsd.du_an'].browse(vals['bsd_du_an_id'])
            sequence = du_an.get_ma_bo_cn(loai_cn=self._name)
        if not sequence:
            raise UserError(_('Dự án chưa có mã cập nhật giá trị QSDĐ.'))
        vals['bsd_ma'] = sequence.next_by_id()
        return super(BsdCapNhatGTQSDD, self).create(vals)

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


class BsdCapNhatGTQSDDUnit(models.Model):
    _name = 'bsd.cn_qsdd_unit'
    _description = "Cập nhật điều kiện bàn giao sản phẩm"
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _rec_name = 'bsd_unit_id'

    bsd_cn_qsdd_id = fields.Many2one('bsd.cn_qsdd', ondelete='cascade',
                                     string="Cập nhật QSDĐ",
                                     help="Tên cập nhật giá trị QSDĐ", required=True,
                                     readonly=True,
                                     states={'nhap': [('readonly', False)]})
    bsd_ngay = fields.Date(string="Ngày tạo", required=True, default=lambda self: fields.Datetime.now(),
                           readonly=True,
                           states={'nhap': [('readonly', False)]})
    bsd_du_an_id = fields.Many2one('bsd.du_an', string="Dự án", readonly=True)
    bsd_unit_id = fields.Many2one('product.product', string="Sản phẩm", required=True,
                                  readonly=True,
                                  states={'nhap': [('readonly', False)]})
    bsd_hd_ban_id = fields.Many2one('bsd.hd_ban', string="Hợp đồng", readonly=True)
    bsd_qsdd_m2_ht = fields.Monetary(string="QSDĐ/ m2 hiện tại", help="Giá trị QSDĐ/ m2 hiện tại", readonly=True)
    bsd_qsdd_m2_moi = fields.Monetary(string="QSDĐ/ m2 mới", help="Giá trị QSDĐ/ m2 mới", readonly=True,
                                      states={'nhap': [('readonly', False)]})
    bsd_ngay_xn = fields.Datetime(string="Ngày xác nhận", readonly=True, help="Ngày xác nhận")
    bsd_nguoi_xn_id = fields.Many2one('res.users', string="Người xác nhận", readonly=True, help="Ngày xác nhận")
    bsd_ly_do = fields.Char(string="Lý do hủy", help="Lý do hủy", readonly=True)
    state = fields.Selection([('nhap', 'Nháp'), ('xac_nhan', 'Xác nhận'),
                              ('duyet', 'Duyệt'), ('huy', 'Hủy')],
                             string="Trạng thái", default="nhap", required=True, readonly=True, tracking=1)
    company_id = fields.Many2one('res.company', string='Công ty', default=lambda self: self.env.company)
    currency_id = fields.Many2one(related="company_id.currency_id", string="Tiền tệ", readonly=True)

    @api.onchange('bsd_unit_id')
    def _onchange_unit(self):
        self.bsd_du_an_id = self.bsd_unit_id.bsd_du_an_id
        self.bsd_hd_ban_id = self.bsd_unit_id.bsd_hd_ban_id
        self.bsd_qsdd_m2_ht = self.bsd_unit_id.bsd_qsdd_m2

    @api.model
    def create(self, vals):
        res = super(BsdCapNhatGTQSDDUnit, self).create(vals)
        res.write({
            'bsd_du_an_id': res.bsd_unit_id.bsd_du_an_id.id,
            'bsd_hd_ban_id': res.bsd_unit_id.bsd_hd_ban_id.id,
            'bsd_qsdd_m2_ht': res.bsd_unit_id.bsd_qsdd_m2,
        })
        return res