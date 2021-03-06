# -*- conding:utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError
import logging
_logger = logging.getLogger(__name__)


class BsdChuyenGiuCho(models.Model):
    _name = 'bsd.chuyen_ut_gc'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _rec_name = 'bsd_ma'
    _description = 'Phiếu chuyển độ ưu tiên giữ chỗ'

    bsd_ma = fields.Char(string="Mã", help="Mã phiếu chuyển độ ưu tiên giữ chỗ", required=True,
                         readonly=True, copy=False, default='/')
    _sql_constraints = [
        ('bsd_ma_unique', 'unique (bsd_ma)',
         'Mã phiếu chuyển độ ưu tiên đã tồn tại !')]
    bsd_ngay = fields.Date(string="Ngày", help="Ngày tạo", default=lambda self: fields.Date.today(),
                           readonly=True,
                           states={'nhap': [('readonly', False)]})
    bsd_du_an_id = fields.Many2one("bsd.du_an", string="Dự án", help="Dự án", required=True,
                                   readonly=True,
                                   states={'nhap': [('readonly', False)]})
    bsd_loai_gc = fields.Selection([('gc_tc', 'Giữ chỗ thiện chí'),
                                    ('giu_cho', 'Giữ chỗ')], string="Loại giữ chỗ", required=True,
                                   help="Loại phiếu giữ chỗ", default="gc_tc",
                                   readonly=True,
                                   states={'nhap': [('readonly', False)]})
    bsd_unit_id = fields.Many2one('product.product', string="Sản phẩm", readonly=True,
                                  states={'nhap': [('readonly', False)]})
    bsd_gc_tc_ch_id = fields.Many2one('bsd.gc_tc', string="GCTC cần chuyển",
                                      help="Phiếu giữ chỗ thiện chí cần chuyển",
                                      readonly=True,
                                      states={'nhap': [('readonly', False)]})
    bsd_kh_ch_id = fields.Many2one('res.partner', string="KH cần chuyển",
                                   readonly=True,
                                   states={'nhap': [('readonly', False)]})
    bsd_stt_ch = fields.Integer(string="Số TT cần chuyển",
                                readonly=True,
                                states={'nhap': [('readonly', False)]})
    bsd_ngay_ch = fields.Date(string="Ngày ut cần chuyển", readonly=True,
                              states={'nhap': [('readonly', False)]})
    bsd_kh_dc_id = fields.Many2one('res.partner', string="KH được chuyển",
                                   readonly=True,
                                   states={'nhap': [('readonly', False)]})
    bsd_stt_dc = fields.Integer(string="Số TT được chuyển",
                                readonly=True,
                                states={'nhap': [('readonly', False)]})
    bsd_ngay_dc = fields.Date(string="Ngày UT được chuyển", readonly=True,
                              states={'nhap': [('readonly', False)]})

    @api.onchange('bsd_loai_gc', 'bsd_gc_tc_ch_id', 'bsd_giu_cho_ch_id',
                  'bsd_gc_tc_dc_id', 'bsd_giu_cho_dc_id')
    def _onchange_giu_cho(self):
        if self.bsd_loai_gc == 'gc_tc':
            self.bsd_kh_ch_id = self.bsd_gc_tc_ch_id.bsd_khach_hang_id
            self.bsd_stt_ch = self.bsd_gc_tc_ch_id.bsd_stt
            self.bsd_ngay_ch = self.bsd_gc_tc_ch_id.bsd_ngay_ut
            self.bsd_kh_dc_id = self.bsd_gc_tc_dc_id.bsd_khach_hang_id
            self.bsd_stt_dc = self.bsd_gc_tc_dc_id.bsd_stt
            self.bsd_ngay_dc = self.bsd_gc_tc_dc_id.bsd_ngay_ut
        else:
            self.bsd_kh_ch_id = self.bsd_giu_cho_ch_id.bsd_khach_hang_id
            self.bsd_stt_ch = self.bsd_giu_cho_ch_id.bsd_stt_bg
            self.bsd_ngay_ch = self.bsd_giu_cho_ch_id.bsd_ngay_hh_bg
            self.bsd_kh_dc_id = self.bsd_giu_cho_dc_id.bsd_khach_hang_id
            self.bsd_stt_dc = self.bsd_giu_cho_dc_id.bsd_stt_bg
            self.bsd_ngay_dc = self.bsd_giu_cho_dc_id.bsd_ngay_hh_bg
    bsd_gc_tc_dc_id = fields.Many2one('bsd.gc_tc', string="GCTC được chuyển",
                                      help="Phiếu giữ chỗ thiện chí được chuyển",
                                      readonly=True,
                                      states={'nhap': [('readonly', False)]})
    bsd_giu_cho_ch_id = fields.Many2one('bsd.giu_cho', string="GC cần chuyển", help="Giữ chỗ cần chuyển",
                                        readonly=True,
                                        states={'nhap': [('readonly', False)]})
    bsd_giu_cho_dc_id = fields.Many2one('bsd.giu_cho', string="GC được chuyển", help="Giữ chỗ được chuyển",
                                        readonly=True,
                                        states={'nhap': [('readonly', False)]})
    bsd_dien_giai = fields.Char(string="Diễn giải", help="Diễn giải",
                                readonly=True,
                                states={'nhap': [('readonly', False)]})
    bsd_ly_do = fields.Char(string="Lý do", readonly=True)
    bsd_nguoi_duyet_id = fields.Many2one('res.users', string="Người duyệt", readonly=True)
    bsd_ngay_duyet = fields.Date(string="Ngày duyệt", readonly=True)
    state = fields.Selection([('nhap', 'Nháp'), ('xac_nhan', 'Xác nhận'),
                              ('duyet', 'Duyệt'), ('huy', 'Hủy')], string="Trạng thái", help="Trạng thái",
                             required=True, default='nhap', tracking=1)

    def action_xac_nhan(self):
        if self.bsd_loai_gc == 'gc_tc':
            if not self.bsd_gc_tc_dc_id or not self.bsd_gc_tc_ch_id:
                raise UserError("Chưa chọn giữ chỗ thiện chí.\nVui lòng kiểm tra lại thông tin.")
            if self.bsd_gc_tc_dc_id.state != 'huy':
                raise UserError("Giữ chỗ thiện chí chưa hủy.\nVui lòng kiểm tra lại thông tin.")
            if self.bsd_gc_tc_ch_id.state not in ['cho_rc', 'giu_cho']:
                raise UserError("Phiếu giữ chỗ thiện chí chưa thanh toán đủ.\nVui lòng kiểm tra lại thông tin.")
        else:
            if not self.bsd_giu_cho_dc_id or not self.bsd_giu_cho_ch_id:
                raise UserError("Chưa chọn giữ chỗ thiện chí.\nVui lòng kiểm tra lại thông tin.")
            if self.bsd_giu_cho_dc_id.state != 'huy':
                raise UserError("Giữ chỗ thiện chí chưa hủy.\nVui lòng kiểm tra lại thông tin.")
            if self.bsd_giu_cho_ch_id.state not in ['dang_cho', 'giu_cho']:
                raise UserError("Phiếu giữ chỗ thiện chí chưa thanh toán đủ.\nVui lòng kiểm tra lại thông tin.")
        if self.state == 'nhap':
            self.write({
                'state': 'xac_nhan',
            })

    def action_duyet(self):
        if self.state == 'xac_nhan':
            self.write({
                'state': 'duyet',
                'bsd_ngay_duyet': fields.Date.today(),
                'bsd_nguoi_duyet_id': self.env.uid,
                'bsd_ly_do': '',
            })
        if self.bsd_loai_gc == 'gc_tc':
            if self.bsd_gc_tc_dc_id.state != 'huy':
                raise UserError("Giữ chỗ thiện chí chưa hủy.\nVui lòng kiểm tra lại thông tin.")
            if self.bsd_gc_tc_ch_id.state not in ['cho_rc', 'giu_cho']:
                raise UserError("Phiếu giữ chỗ thiện chí chưa thanh toán đủ.\nVui lòng kiểm tra lại thông tin.")
            self.bsd_gc_tc_ch_id.write({
                'bsd_stt': self.bsd_gc_tc_dc_id.bsd_stt,
                'bsd_ngay_ut': self.bsd_gc_tc_dc_id.bsd_ngay_ut
            })
            # Cập nhật lại trạng thái giữ chỗ
            # Lấy giữ chỗ đã có trạng thái là giữ chỗ của dự án
            gc_tc_dang_uu_tien = self.env['bsd.gc_tc'].search([('bsd_du_an_id', '=', self.bsd_du_an_id.id),
                                                                 ('state', '=', 'giu_cho')], limit=1)
            # Kiểm tra ngày thứ tự của giữ chỗ dc chuyển có nhỏ hơn giữ chỗ đang ưu tiên hay ko
            if self.bsd_gc_tc_ch_id.bsd_ngay_ut < gc_tc_dang_uu_tien.bsd_ngay_ut:
                self.bsd_gc_tc_ch_id.write({
                    'state': 'giu_cho'
                })
                gc_tc_dang_uu_tien.write({
                    'state': 'cho_rc'
                })
        else:
            if self.bsd_giu_cho_dc_id.state != 'huy':
                raise UserError("Giữ chỗ thiện chí chưa hủy.\nVui lòng kiểm tra lại thông tin.")
            if self.bsd_giu_cho_ch_id.state not in ['dang_cho', 'giu_cho']:
                raise UserError("Phiếu giữ chỗ thiện chí chưa thanh toán đủ.\nVui lòng kiểm tra lại thông tin.")
            self.bsd_giu_cho_ch_id.write({
                'bsd_stt_bg': self.bsd_giu_cho_dc_id.bsd_stt_bg,
                'bsd_ngay_hh_bg': self.bsd_giu_cho_dc_id.bsd_ngay_hh_bg
            })
            # Cập nhật lại trạng thái giữ chỗ
            # Lấy giữ chỗ đã có trạng thái là giữ chỗ của dự án
            giu_cho_dang_uu_tien = self.env['bsd.giu_cho'].search([('bsd_du_an_id', '=', self.bsd_du_an_id.id),
                                                                   ('bsd_unit_id', '=', self.bsd_unit_id.id),
                                                                   ('state', '=', 'giu_cho')], limit=1)
            # Kiểm tra ngày thứ tự của giữ chỗ dc chuyển có nhỏ hơn giữ chỗ đang ưu tiên hay ko
            if self.bsd_giu_cho_ch_id.bsd_ngay_hh_bg < giu_cho_dang_uu_tien.bsd_ngay_hh_bg:
                self.bsd_giu_cho_ch_id.write({
                    'state': 'giu_cho'
                })
                giu_cho_dang_uu_tien.write({
                    'state': 'dang_cho'
                })

    def action_khong_duyet(self):
        action = self.env.ref('bsd_kinh_doanh.bsd_wizard_chuyen_ut_gc_action').read()[0]
        return action

    # KD.05.07.04 Hủy chuyển độ ưu tiên giữ chỗ
    def action_huy(self):
        self.write({
            'state': 'huy'
        })

    @api.model
    def create(self, vals):
        sequence = False
        if 'bsd_du_an_id' in vals:
            du_an = self.env['bsd.du_an'].browse(vals['bsd_du_an_id'])
            sequence = du_an.get_ma_bo_cn(loai_cn=self._name)
        if not sequence:
            raise UserError(_('Dự án chưa có mã phiếu chuyển độ ưu tiên giữ chỗ.'))
        vals['bsd_ma'] = sequence.next_by_id()
        return super(BsdChuyenGiuCho, self).create(vals)
