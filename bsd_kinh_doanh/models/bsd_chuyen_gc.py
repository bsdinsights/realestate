# -*- conding:utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError
import logging
_logger = logging.getLogger(__name__)


class BsdChuyenGiuCho(models.Model):
    _name = 'bsd.chuyen_gc'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _rec_name = 'bsd_ma_chuyen_gc'
    _description = 'Phiếu chuyển tên khách hàng giữ chỗ'

    bsd_ma_chuyen_gc = fields.Char(string="Mã", help="Mã phiếu đề nghị chuyển tên", required=True, readonly=True, copy=False,
                                   default='/')
    _sql_constraints = [
        ('bsd_ma_chuyen_gc_unique', 'unique (bsd_ma_chuyen_gc)',
         'Mã phiếu chuyển tên đã tồn tại !')]
    bsd_ngay = fields.Date(string="Ngày", help="Ngày chuyển tên", default=lambda self: fields.Date.today(),
                                  readonly=True,
                                  states={'nhap': [('readonly', False)]})
    bsd_du_an_id = fields.Many2one("bsd.du_an", string="Dự án", help="Dự án", required=True,
                                   readonly=True,
                                   states={'nhap': [('readonly', False)]})
    bsd_kh_ht_id = fields.Many2one("res.partner", string="Khách hàng hiện tại", help="Khách hàng trên phiếu giữ chỗ",
                                   required=True,
                                   readonly=True,
                                   states={'nhap': [('readonly', False)]})
    bsd_loai_gc = fields.Selection([('gc_tc', 'Giữ chỗ thiện chí'),
                                    ('giu_cho', 'Giữ chỗ')], string="Loại giữ chỗ", required=True,
                                   help="Loại phiếu giữ chỗ", default="gc_tc",
                                   readonly=True,
                                   states={'nhap': [('readonly', False)]})
    bsd_gc_tc_id = fields.Many2one('bsd.gc_tc', string="Giữ chỗ thiện chí",
                                   help="Phiếu giữ chỗ thiện chí",
                                   readonly=True,
                                   states={'nhap': [('readonly', False)]})
    bsd_giu_cho_id = fields.Many2one('bsd.giu_cho', string="Giữ chỗ", help="Giữ chỗ",
                                     readonly=True,
                                     states={'nhap': [('readonly', False)]})
    bsd_unit_id = fields.Many2one('product.product', related="bsd_giu_cho_id.bsd_unit_id")
    bsd_kh_moi_id = fields.Many2one('res.partner', string="Khách hàng mới", help="Khách hàng được chuyển giữ chỗ",
                                    required=True,
                                    readonly=True,
                                    states={'nhap': [('readonly', False)]})
    bsd_dien_giai = fields.Char(string="Diễn giải", help="Diễn giải",
                                readonly=True,
                                states={'nhap': [('readonly', False)]})
    bsd_ly_do = fields.Char(string="Lý do", readonly=True, tracking=2)

    state = fields.Selection([('nhap', 'Nháp'), ('xac_nhan', 'Xác nhận'),
                              ('da_duyet', 'Đã duyệt'), ('huy', 'Hủy')], string="Trạng thái", help="Trạng thái",
                             required=True, default='nhap', tracking=1)

    # KD.05.07.01 Xác nhận phiếu chuyển tên khách hàng giữ chỗ
    def action_xac_nhan(self):
        self.write({
            'state': 'xac_nhan',
        })

    # KD.05.07.02 Duyệt chuyển tên khách hàng giữ chỗ
    def action_duyet(self):
        self.write({
            'state': 'da_duyet',
        })
        if self.bsd_loai_gc == 'gc_tc' and self.bsd_gc_tc_id:
            if self.bsd_gc_tc_id.state not in ['cho_rc', 'giu_cho']:
                raise UserError("Giữ chỗ thiện chí đã hết hiệu lực hoặc đã ráp căn.\n Vui lòng kiểm tra lại thông tin.")
            if self.bsd_gc_tc_id.bsd_thanh_toan != 'da_tt':
                raise UserError("Phiếu giữ chỗ thiện chí chưa thanh toán đủ.\n Vui lòng kiểm tra lại thông tin.")
            self.bsd_gc_tc_id.write({
                'bsd_kh_moi_id': self.bsd_kh_moi_id.id,
            })
        if self.bsd_loai_gc == 'giu_cho' and self.bsd_giu_cho_id:
            if self.bsd_giu_cho_id.state not in ['dang_cho', 'giu_cho']:
                raise UserError("Giữ chỗ đã hết hiệu lực.\n Vui lòng kiểm tra lại thông tin.")
            if self.bsd_giu_cho_id.bsd_thanh_toan != 'da_tt':
                raise UserError("Phiếu giữ chỗ chưa thanh toán đủ.\n Vui lòng kiểm tra lại thông tin.")
            self.bsd_giu_cho_id.write({
                'bsd_kh_moi_id': self.bsd_kh_moi_id.id,
            })

    # KD.05.07.03 Từ chối yêu cầu chuyển tên khách hàng giữ chỗ
    def action_khong_duyet(self):
        _logger.debug("không duyệt")
        action = self.env.ref('bsd_kinh_doanh.bsd_wizard_chuyen_gc_action').read()[0]
        return action

    # KD.05.07.04 Hủy chuyển tên khách hàng giữ chỗ
    def action_huy(self):
        self.write({
            'state': 'huy'
        })

    @api.model
    def create(self, vals):
        sequence = False
        if vals.get('bsd_ma_chuyen_gc', '/') == '/':
            sequence = self.env['bsd.ma_bo_cn'].search([('bsd_loai_cn', '=', 'bsd.chuyen_gc')], limit=1).bsd_ma_tt_id
            vals['bsd_ma_chuyen_gc'] = self.env['ir.sequence'].next_by_code('bsd.chuyen_gc') or '/'
        if not sequence:
            raise UserError(_('Danh mục mã chưa khai báo mã chương trình khuyến mãi.'))
        vals['bsd_ma_chuyen_gc'] = sequence.next_by_id()
        return super(BsdChuyenGiuCho, self).create(vals)