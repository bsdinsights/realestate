# -*- coding:utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError


class BsdMaBoChungTu(models.Model):
    _name = 'bsd.ma_bo_cn_chung'
    _description = "Cách đánh mã chứng từ dùng chung hệ thống"
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _rec_name = 'bsd_ten_cn'
    _order = 'bsd_loai_cn'

    bsd_ten_cn = fields.Char(string="Tên", help="Tên bộ chứng từ", required=True,
                             readonly=True,
                             states={'nhap': [('readonly', False)]})
    bsd_loai_cn = fields.Selection([('bsd.kh_cn', 'Khách hàng cá nhân'),
                                    ('bsd.kh_dn', 'Khách hàng doanh nghiệp')],
                                   string="Loại chứng từ", help="Loại chứng từ được đặt mã", required=True,
                                   readonly=True,
                                   states={'nhap': [('readonly', False)]})
    bsd_ma_cn = fields.Char(string="Mã tiền tố", help="Mã tiền tố của chứng từ", required=True,
                            readonly=True,
                            states={'nhap': [('readonly', False)]})
    _sql_constraints = [
        ('bsd_ma_cn_unique', 'unique (bsd_ma_cn)',
         'Mã tiền tố chứng từ đã tồn tại !'),
    ]
    bsd_ma_ht = fields.Char(string="Mã hậu tố", help="Mã hậu tố của chứng từ",
                            readonly=True,
                            states={'nhap': [('readonly', False)]})
    bsd_sl_ky_tu = fields.Integer(string="Độ dài chuỗi", help="Độ dài chuổi ký tự sinh tự động của hệ thống",
                                  required=True,
                                  readonly=True,
                                  states={'nhap': [('readonly', False)]})

    @api.constrains('bsd_sl_ky_tu')
    def _constrains_sl_kt(self):
        for each in self:
            if each.bsd_sl_ky_tu < 2:
                raise UserError(_("Độ dài chuỗi ký tự phải lớn hơn 2.\nvui lòng kiểm tra lại thông tin"))
    bsd_ma_tt_id = fields.Many2one('ir.sequence', string="Mã trình tự", help="Mã của trình tự", required=True)
    bsd_so_tt = fields.Integer(string='Số tiếp theo', help="Số tiếp theo được sử dụng",
                               compute='_compute_seq_number_next', inverse='_inverse_seq_number_next',
                               readonly=True,
                               states={'nhap': [('readonly', False)]})
    state = fields.Selection([('nhap', 'Nháp'),
                              ('active', 'Áp dụng'),
                              ('deactive', 'Ngưng sử dụng')],
                             string="Trạng thái", default='nhap', required=True, tracking=1, help="Trạng thái")

    @api.depends('bsd_ma_tt_id.number_next_actual')
    def _compute_seq_number_next(self):
        for each in self:
            if each.bsd_ma_tt_id:
                sequence = each.bsd_ma_tt_id._get_current_sequence()
                each.bsd_so_tt = sequence.number_next_actual
            else:
                each.bsd_so_tt = 1

    def _inverse_seq_number_next(self):
        for each in self:
            if each.bsd_ma_tt_id and each.bsd_so_tt:
                sequence = each.bsd_ma_tt_id._get_current_sequence()
                sequence.sudo().number_next = each.bsd_so_tt

    @api.model
    def _create_sequence(self, vals):
        prefix = vals['bsd_ma_cn']
        suffix = vals['bsd_ma_ht']
        seq = {
            'name': _('%s trình tự') % vals['bsd_ten_cn'],
            'implementation': 'no_gap',
            'prefix': prefix,
            'suffix': suffix,
            'padding': vals['bsd_sl_ky_tu'],
            'number_increment': 1,
        }
        seq = self.env['ir.sequence'].create(seq)
        return seq

    @api.model
    def create(self, vals):
        if not vals.get('bsd_ma_tt_id'):
            vals.update({'bsd_ma_tt_id': self.sudo()._create_sequence(vals).id})
        return super(BsdMaBoChungTu, self).create(vals)

    def write(self, vals):
        if 'bsd_ten_cn' in vals.keys():
            self.bsd_ma_tt_id.write({
                'name': _('%s trình tự') % vals['bsd_ten_cn'],
            })
        if 'bsd_ma_cn' in vals.keys():
            self.bsd_ma_tt_id.write({
                'prefix': vals['bsd_ma_cn'],
            })
        if 'bsd_ma_ht' in vals.keys():
            self.bsd_ma_tt_id.write({
                'suffix': vals['bsd_ma_ht'],
            })
        if 'bsd_sl_ky_tu' in vals.keys():
            self.bsd_ma_tt_id.write({
                'padding': vals['bsd_sl_ky_tu'],
            })
        return super(BsdMaBoChungTu, self).write(vals)