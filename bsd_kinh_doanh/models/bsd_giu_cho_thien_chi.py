# -*- coding:utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError
import datetime
import logging
_logger = logging.getLogger(__name__)


class BsdGiuChoThienChi(models.Model):
    _name = 'bsd.gc_tc'
    _description = 'Giữ chỗ thiện chí'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _rec_name = 'bsd_ma_gctc'

    bsd_ma_gctc = fields.Char(string="Mã giữ chỗ", help="Mã giữ chỗ thiện chí",
                              required=True, readonly=True, copy=False, default='/')
    _sql_constraints = [
        ('bsd_ma_gctc_unique', 'unique (bsd_ma_gctc)', 'Mã giữ chỗ thiện chí đã tồn tại !'),
    ]
    bsd_stt = fields.Integer(string="Số thứ tự", readonly=1)
    bsd_ngay_gctc = fields.Datetime(string="Ngày giữ chỗ", required=True, help="Ngày giữ chỗ thiện chí",
                                    readonly=True, default=lambda self: fields.Datetime.now())
    bsd_khach_hang_id = fields.Many2one('res.partner', string="Khách hàng", required=True,
                                        readonly=True, help="Khách hàng",
                                        states={'nhap': [('readonly', False)]})
    bsd_du_an_id = fields.Many2one('bsd.du_an', string="Dự án", required=True,
                                   readonly=True, help="Tên dự án",
                                   states={'nhap': [('readonly', False)]})
    bsd_tien_gc = fields.Monetary(string="Tiền giữ chỗ", help="Tiền giữ chỗ thiện chí", required=True,
                                  readonly=True,
                                  states={'nhap': [('readonly', False)]})

    @api.onchange('bsd_du_an_id')
    def _onchange_tien_gc(self):
        self.bsd_tien_gc = self.bsd_du_an_id.bsd_tien_gc

    bsd_dien_giai = fields.Char(string="Diễn giải",
                                readonly=True, help="Diễn giải",
                                states={'nhap': [('readonly', False)]})

    def _get_nhan_vien(self):
        return self.env['hr.employee'].search([('user_id', '=', self.env.uid)])

    bsd_nvbh_id = fields.Many2one('hr.employee', string="Nhân viên KD", help="Nhân viên kinh doanh",
                                  readonly=True, required=True, default=_get_nhan_vien,
                                  states={'nhap': [('readonly', False)]})
    bsd_san_gd_id = fields.Many2one('res.partner', string="Sàn giao dịch", domain=[('is_company', '=', True)],
                                    readonly=True, help='Sàn giao dịch',
                                    states={'nhap': [('readonly', False)]})
    bsd_ctv_id = fields.Many2one('res.partner', string="Cộng tác viên", domain=[('is_company', '=', False)],
                                 readonly=True, help="Cộng tác viên",
                                 states={'nhap': [('readonly', False)]})
    bsd_gioi_thieu_id = fields.Many2one('res.partner', string="Giới thiệu", help="Cá nhân hoặc đơn vị giới thiệu",
                                        readonly=True,
                                        states={'nhap': [('readonly', False)]})
    bsd_ngay_hh_gctc = fields.Datetime(string="Hạn giữ chỗ", help="Hiệu lực của giữ chỗ",
                                       readonly=True,
                                       required=True,
                                       tracking=3)

    @api.onchange('bsd_ngay_gctc', 'bsd_du_an_id')
    def _onchange_ngay_gctc(self):
        self.bsd_ngay_hh_gctc = self.bsd_ngay_gctc + datetime.timedelta(hours=self.bsd_du_an_id.bsd_gc_smb)

    bsd_ngay_ut = fields.Datetime(string="Ngày thứ tự", readonly=True,
                                  help="Thời gian được sử dụng để xét ưu tiên khi làm phiếu ráp căn")
    bsd_het_han = fields.Boolean(string="Hết hạn", help="Giữ chỗ bị hết hạn sau khi thanh toán đủ",
                                 readonly=True)
    bsd_ngay_rc = fields.Datetime(string="Ngày ráp căn", help="Ngày thực tế ráp căn", readonly=True)
    bsd_ngay_huy_rc = fields.Datetime(string="Hủy ráp căn", help="Ngày hủy ráp căn", readonly=True)
    bsd_rap_can_id = fields.Many2one('bsd.rap_can', string="Ráp căn", help="Phiếu ráp căn", readonly=True)
    state = fields.Selection([('nhap', 'Nháp'),
                              ('xac_nhan', 'Xác nhận'),
                              ('cho_rc', 'Đang chờ'),
                              ('giu_cho', 'Giữ chỗ'),
                              ('dong_gc', 'Đóng'),
                              ('het_han', 'Hết hạn'),
                              ('huy', 'Hủy')], string="Trạng thái", default="nhap", tracking=1,
                             required=True, readonly=True)
    company_id = fields.Many2one('res.company', string='Công ty', default=lambda self: self.env.company)
    currency_id = fields.Many2one(related="company_id.currency_id", string="Tiền tệ", readonly=True)

    bsd_thanh_toan = fields.Selection([('chua_tt', 'Chưa thanh toán'),
                                       ('dang_tt', 'Đang thanh toán'),
                                       ('da_tt', 'Đã thanh toán')], string="Thanh toán", default="chua_tt",
                                      required=True, readonly=True)
    bsd_ngay_tt = fields.Datetime(string="Ngày thanh toán", help="Ngày (kế toán xác nhận) thanh toán giữ chỗ",
                                  readonly=True)

    bsd_kh_moi_id = fields.Many2one('res.partner', string="KH chuyển tên", help="Người được chuyển tên giữ chỗ",
                                    tracking=2, readonly=True)
    bsd_huy_gc_id = fields.Many2one('bsd.huy_gc', string="Hủy giữ chỗ",
                                    help="Mã phiếu hủy giữ chỗ thiện chí được duyệt", readonly=1)
    bsd_so_huy_gc = fields.Integer(string="# Hủy giữ chỗ", compute='_compute_huy_gc')
    bsd_so_rap_can = fields.Integer(string="# Ráp căn", compute='_compute_rap_can')

    @api.onchange('bsd_nvbh_id')
    def _onchange_san_ctv(self):
        res = {}
        self.env.cr.execute("""SELECT bsd_cn_id FROM bsd_loai_cn_rel 
                                WHERE bsd_loai_id = {0}
                            """.format(self.env.ref('bsd_kinh_doanh.bsd_ctv').id))
        _logger.debug("onchange san ctv")
        list_cn = [cn[0] for cn in self.env.cr.fetchall()]
        self.env.cr.execute("""SELECT bsd_dn_id FROM bsd_loai_dn_rel 
                                WHERE bsd_loai_id = {0}
                            """.format(self.env.ref('bsd_kinh_doanh.bsd_san').id))
        list_dn = [cn[0] for cn in self.env.cr.fetchall()]
        res.update({
            'domain': {
                'bsd_ctv_id': [('id', 'in', list_cn)],
                'bsd_san_gd_id': [('id', 'in', list_dn)]
            }
        })
        return res

    # 3 field ctv , sàn gd, giới thiệu không tồn tại đồng thời
    # Khách hàng không được trùng với mô giới
    @api.constrains('bsd_ctv_id', 'bsd_san_gd_id', 'bsd_gioi_thieu_id', 'bsd_khach_hang_id')
    def _constrains_mo_gioi(self):
        if (self.bsd_ctv_id and self.bsd_san_gd_id) \
            or (self.bsd_ctv_id and self.bsd_gioi_thieu_id) \
               or (self.bsd_san_gd_id and self.bsd_gioi_thieu_id):
            raise UserError("Vui lòng chọn 1 trong 3 giá trị: Sàn giao dịch, Công tác viên, Khách hàng giới thiệu, ")
        if self.bsd_khach_hang_id == self.bsd_ctv_id \
            or self.bsd_khach_hang_id == self.bsd_san_gd_id \
                or self.bsd_khach_hang_id == self.bsd_gioi_thieu_id:
            raise UserError("Khách hàng không thể trùng với người môi giới")

    @api.constrains('bsd_tien_gc')
    def _check_bsd_tien_gc(self):
        for record in self:
            if record.bsd_tien_gc < 0:
                raise ValidationError("Tiền giữ chỗ phải lớn hơn 0")

    def _compute_huy_gc(self):
        for each in self:
            huy_gc = self.env['bsd.huy_gc'].search([('bsd_gc_tc_id', '=', self.id)])
            each.bsd_so_huy_gc = len(huy_gc)

    def action_view_huy_gc(self):
        action = self.env.ref('bsd_kinh_doanh.bsd_huy_gc_action').read()[0]

        huy_gc = self.env['bsd.huy_gc'].search([('bsd_gc_tc_id', '=', self.id)])
        if len(huy_gc) > 1:
            action['domain'] = [('id', 'in', huy_gc.ids)]
        elif huy_gc:
            form_view = [(self.env.ref('bsd_kinh_doanh.bsd_huy_gc_form').id, 'form')]
            if 'views' in action:
                action['views'] = form_view + [(state, view) for state, view in action['views'] if view != 'form']
            else:
                action['views'] = form_view
            action['res_id'] = huy_gc.id
        # Prepare the context.
        context = {
            'default_bsd_khach_hang_id': self.bsd_khach_hang_id.id,
            'default_bsd_gc_tc_id': self.id,
            'default_bsd_du_an_id': self.bsd_du_an_id.id,
            'default_loai_gc': 'gc_tc'
        }
        action['context'] = context
        return action

    def _compute_rap_can(self):
        for each in self:
            rap_can = self.env['bsd.rap_can'].search([('bsd_gc_tc_id', '=', self.id)])
            each.bsd_so_rap_can = len(rap_can)

    def action_view_rap_can(self):
        action = self.env.ref('bsd_kinh_doanh.bsd_rap_can_action').read()[0]

        rap_can = self.env['bsd.rap_can'].search([('bsd_gc_tc_id', '=', self.id)])
        if len(rap_can) > 1:
            action['domain'] = [('id', 'in', rap_can.ids)]
        elif rap_can:
            form_view = [(self.env.ref('bsd_kinh_doanh.bsd_rap_can_form').id, 'form')]
            if 'views' in action:
                action['views'] = form_view + [(state, view) for state, view in action['views'] if view != 'form']
            else:
                action['views'] = form_view
            action['res_id'] = rap_can.id
        # Prepare the context.
        context = {
            'default_bsd_khach_hang_id': self.bsd_khach_hang_id.id,
            'default_bsd_gc_tc_id': self.id,
            'default_bsd_du_an_id': self.bsd_du_an_id.id,
            'default_loai_gc': 'gc_tc'
        }
        action['context'] = context
        return action

    # KD.05.06 Quản lý số lượng giữ chỗ theo nhân viên bán hàng
    @api.constrains('bsd_nvbh_id')
    def _constrain_nv_bh(self):
        min_time = datetime.datetime.combine(datetime.date.today(), datetime.datetime.min.time())
        max_time = datetime.datetime.combine(datetime.date.today(), datetime.datetime.max.time())
        gc_in_day = self.env['bsd.gc_tc'].search([('create_date', '<', max_time),
                                                  ('create_date', '>', min_time),
                                                  ('bsd_du_an_id', '=', self.bsd_du_an_id.id),
                                                  ('bsd_nvbh_id', '=', self.bsd_nvbh_id.id),
                                                  ('state', '=', 'xac_nhan'),
                                                  ('bsd_thanh_toan', 'in', ['chua_tt', 'dang_tt'])])
        if len(gc_in_day) >= self.bsd_du_an_id.bsd_gc_nv_ngay:
            raise UserError("Số lượng giữ chỗ tối đa trên một ngày của bạn đã vượt mức.\n Vui lòng kiểm tra lại")

    # KD.05.08 Theo dõi công nợ giữ chỗ thiện chí
    def _tao_rec_cong_no(self):
        self.env['bsd.cong_no'].create({
            'bsd_chung_tu': self.bsd_ma_gctc,
            'bsd_ngay': self.bsd_ngay_gctc,
            'bsd_khach_hang_id': self.bsd_khach_hang_id.id,
            'bsd_du_an_id': self.bsd_du_an_id.id,
            'bsd_ps_tang': self.bsd_tien_gc,
            'bsd_ps_giam': 0,
            'bsd_loai_ct': 'gc_tc',
            'bsd_phat_sinh': 'tang',
            'bsd_gc_tc_id': self.id,
            'state': 'da_gs',
        })

    # KD.05.01 Xác nhận giữ chỗ thiện chí
    def action_xac_nhan(self):
        self._tao_rec_cong_no()
        now = datetime.datetime.now()
        ngay_gctc = now
        ngay_hh_gctc = ngay_gctc + datetime.timedelta(hours=self.bsd_du_an_id.bsd_gc_smb)
        self.write({
            'state': 'xac_nhan',
            'bsd_ngay_gctc': ngay_gctc,
            'bsd_ngay_hh_gctc': ngay_hh_gctc,
        })

    # KD.05.02 Hủy giữ chỗ thiện chí
    def action_huy(self):
        self.write({
            'state': 'huy',
        })

    # KD.05.03 Tự động hủy giữ chỗ
    # KD.05.04 Tự động đánh dấu hết hạn giữ chỗ
    def auto_huy_giu_cho(self):
        if self.bsd_thanh_toan in ['chua_tt']:
            self.write({
                'state': 'het_han'
            })
        if self.bsd_thanh_toan in ['da_tt', 'dang_tt']:
            self.write({
                'bsd_het_han': True
            })

    # KD.05.09 - Đề nghị hủy giữ chỗ
    def action_de_nghi_huy(self):
        context = {
            'default_bsd_khach_hang_id': self.bsd_khach_hang_id.id,
            'default_bsd_gc_tc_id': self.id,
            'default_bsd_du_an_id': self.bsd_du_an_id.id,
            'default_loai_gc': 'gc_tc',
            'default_bsd_hoan_tien': True
        }
        action = self.env.ref('bsd_kinh_doanh.bsd_huy_gc_action_popup').read()[0]
        action['context'] = context
        return action

    # tiện ích ráp căn
    def action_rap_can(self):
        action = self.env.ref('bsd_kinh_doanh.bsd_rap_can_action_popup').read()[0]
        action['context'] = {
            'default_bsd_gc_tc_id': self.id,
            'default_bsd_khach_hang_id': self.bsd_kh_moi_id.id,
            'default_bsd_du_an_id': self.bsd_du_an_id.id,
        }
        return action

    @api.model
    def create(self, vals):
        sequence = False
        if 'bsd_du_an_id' in vals:
            du_an = self.env['bsd.du_an'].browse(vals['bsd_du_an_id'])
            sequence = du_an.get_ma_bo_cn(loai_cn=self._name)
        if not sequence:
            raise UserError(_('Dự án chưa có mã giữ chỗ thiện chí'))
        # Cập nhật thời gian hết hạn giữ chỗ thiện chí khi tạo mới
        vals['bsd_ma_gctc'] = sequence.next_by_id()

        res = super(BsdGiuChoThienChi, self).create(vals)
        # R11 Chuyển nhượng khách hàng
        res.write({
            'bsd_kh_moi_id': res.bsd_khach_hang_id.id
        })
        return res

    def write(self, vals):
        if 'bsd_khach_hang_id' in vals:
            vals.update({
                'bsd_kh_moi_id': vals['bsd_khach_hang_id']
            })
        res = super(BsdGiuChoThienChi, self).write(vals)
        return res
