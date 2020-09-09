# -*- coding:utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError
import datetime
import logging
_logger = logging.getLogger(__name__)


class BsdGiuCho(models.Model):
    _name = 'bsd.giu_cho'
    _description = "Thông tin giữ chỗ"
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _rec_name = 'bsd_ma_gc'

    bsd_ma_gc = fields.Char(string="Mã giữ chỗ", required=True, readonly=True, copy=False, default='/')
    _sql_constraints = [
        ('bsd_ma_gc_unique', 'unique (bsd_ma_gc)',
         'Mã giữ chỗ đã tồn tại !'),
    ]
    bsd_ngay_gc = fields.Datetime(string="Ngày giữ chỗ", required=True, default=lambda self: fields.Datetime.now(),
                                  readonly=True, help='Ngày giữ chỗ',
                                  states={'nhap': [('readonly', False)]})
    bsd_khach_hang_id = fields.Many2one('res.partner', string="Khách hàng", required=True,
                                        readonly=True, help="Tên khách hàng",
                                        states={'nhap': [('readonly', False)]})
    bsd_du_an_id = fields.Many2one('bsd.du_an', string="Dự án", required=True,
                                   readonly=True, help="Tên dự án",
                                   states={'nhap': [('readonly', False)]})
    bsd_unit_id = fields.Many2one('product.product', string="Sản phẩm", required=True,
                                  readonly=True, help="Tên Sản phẩm",
                                  states={'nhap': [('readonly', False)]})
    bsd_ten_sp = fields.Char(related="bsd_unit_id.name")
    bsd_product_tmpl_id = fields.Many2one(related='bsd_unit_id.product_tmpl_id', store=True)
    bsd_dien_giai = fields.Char(string="Diễn giải",
                                readonly=True, help="Diễn giải",
                                states={'nhap': [('readonly', False)]})
    bsd_truoc_mb = fields.Boolean(string="Trước mở bán", default=False,
                                  help="Thông tin xác định Giữ chỗ được tạo trước hay sau khi unit có đợt mở bán",
                                  readonly=True)
    bsd_dot_mb_id = fields.Many2one('bsd.dot_mb', help="Đợt mở bán", string="Đợt mở bán",
                                    readonly=True,states={'nhap': [('readonly', False)]})

    bsd_bang_gia_id = fields.Many2one('product.pricelist', related="bsd_dot_mb_id.bsd_bang_gia_id", store=True,
                                      string="Bảng giá", help="Bảng giá bán")
    bsd_tien_gc = fields.Monetary(string="Tiền giữ chỗ", required=True,
                                  readonly=True, help="Tiền giữ chỗ",
                                  states={'nhap': [('readonly', False)]})

    def _get_nhan_vien(self):
        return self.env['hr.employee'].search([('user_id', '=', self.env.uid)])

    bsd_nvbh_id = fields.Many2one('hr.employee', string="Nhân viên BH", help="Nhân viên bán hàng",
                                  readonly=True, required=True, default=_get_nhan_vien,
                                  states={'nhap': [('readonly', False)]})
    bsd_san_gd_id = fields.Many2one('res.partner', string="Sàn giao dịch", domain=[('is_company', '=', True)],
                                    readonly=True, help="Sàn giao dịch",
                                    states={'nhap': [('readonly', False)]})
    bsd_ctv_id = fields.Many2one('res.partner', string="Công tác viên", domain=[('is_company', '=', False)],
                                 readonly=True, help="Cộng tác viên",
                                 states={'nhap': [('readonly', False)]})
    bsd_gioi_thieu_id = fields.Many2one('res.partner', string="Giới thiệu", help="Cá nhân hoặc đơn vị giới thiệu",
                                        readonly=True,
                                        states={'nhap': [('readonly', False)]})
    bsd_ngay_hh_gc = fields.Datetime(string="Hạn giữ chỗ", help="Hiệu lực của giữ chỗ", compute='_compute_hl_gc', store=True)
    bsd_gc_da = fields.Boolean(string="Giữ chỗ dự án", help="""Thông tin ghi nhận Giữ chỗ được tự động tạo từ 
                                                                giữ chỗ thiện chí hay không""", readonly=True)
    bsd_gc_tc_id = fields.Many2one('bsd.gc_tc', string="Giữ chỗ thiện chí", readonly=True,
                                   help="Phiếu giữ chỗ thiện chí",)
    bsd_rap_can_id = fields.Many2one('bsd.rap_can', string="Ráp căn", help="Phiếu ráp căn", readonly=True)
    state = fields.Selection([('nhap', 'Nháp'),
                              ('dat_cho', 'Đặt chỗ'),
                              ('giu_cho', 'Giữ chỗ'),
                              ('bao_gia', 'Báo giá'),
                              ('dong', 'Đóng'),
                              ('huy', 'Hủy')], default='nhap', string="Trạng thái",
                             tracking=1, help="Trạng thái", required=True, readonly=True)
    company_id = fields.Many2one('res.company', string='Công ty', default=lambda self: self.env.company)
    currency_id = fields.Many2one(related="company_id.currency_id", string="Tiền tệ", readonly=True)

    bsd_thanh_toan = fields.Selection([('chua_tt', 'Chưa thanh toán'),
                                       ('dang_tt', 'Đang thanh toán'),
                                       ('da_tt', 'Đã thanh toán')], string="Thanh toán", default="chua_tt",
                                      help="Thanh toán",
                                      required=True, readonly=True)
    bsd_ngay_tt = fields.Datetime(string="Ngày thanh toán", help="Ngày (kế toán xác nhận) thanh toán giữ chỗ",readonly=True)
    bsd_stt_bg = fields.Integer(string="STT báo giá", readonly=True, help="Số thứ tự ưu tiên làm báo giá")
    bsd_ngay_hh_bg = fields.Datetime(string="Hạn báo giá", help="Hiệu lực được làm báo giá", readonly=True)
    bsd_het_han_bg = fields.Boolean(string="Hết hạn báo giá", readonly=True, default=False,
                                    help="Thông tin ghi nhận thời gian làm báo giá có bok hết hiệu lực hay chưa")
    bsd_ngay_hh_stt = fields.Datetime(string="Hạn GC sau TT", compute="_compute_ngay_hh_stt", store=True,
                                      help="Ngày hết hạn giữ chỗ sau khi thanh toán tiền giữ chỗ")
    bsd_het_han_gc = fields.Boolean(string="Hết hạn giữ chỗ", readonly=True,
                                    help="""Thông tin ghi nhận giữ chỗ bị hết hiệu lực sau khi đã thanh toán giữ chỗ""")

    bsd_kh_moi_id = fields.Many2one('res.partner', string="KH chuyển tên", help="Người được chuyển tên giữ chỗ",
                                    tracking=2, readonly=True)

    bsd_tien_gctc = fields.Monetary(string="Tiền GCTC", help="Tiền giữ chỗ thiện chí đã thanh toán",
                                    readonly=True, default=0)
    bsd_huy_gc_id = fields.Many2one('bsd.huy_gc', string="Hủy giữ chỗ", help="Mã phiếu hủy giữ chỗ", readonly=1)

    bsd_so_bao_gia = fields.Integer(string="# Báo giá", compute='_compute_bao_gia')
    bsd_so_huy_gc = fields.Integer(string="# Hủy giữ chỗ", compute='_compute_huy_gc')

    # Tên hiện thị record
    def name_get(self):
        res = []
        for gc in self:
            res.append((gc.id, "%s" % gc.bsd_ten_sp))
        return res
    
    @api.model
    def _name_search(self, name='', args=None, operator='ilike', limit=100, name_get_uid=None):
        # private implementation of name_search, allows passing a dedicated user
        # for the name_get part to solve some access rights issues
        args = list(args or [])
        if not (name == '' and operator == 'ilike'):
            args += [('bsd_ten_sp', operator, name)]
        access_rights_uid = name_get_uid or self._uid
        ids = self._search(args, limit=limit, access_rights_uid=access_rights_uid)
        recs = self.browse(ids)
        return models.lazy_name_get(recs.with_user(access_rights_uid))

    @api.constrains('bsd_tien_gc')
    def _check_bsd_tien_gc(self):
        for record in self:
            if record.bsd_tien_gc < 0:
                raise ValidationError("Tiền giữ chỗ phải lớn hơn 0")

    # KD.07.02 Ràng buộc số giữ chỗ theo Sản phẩm/ NVBH
    @api.constrains('bsd_nvbh_id', 'bsd_unit_id')
    def _constrain_unit_nv(self):
        _logger.debug(" Ràng buộc số giữ chỗ theo Sản phẩm/ NVBH")
        gc_in_unit = self.env['bsd.giu_cho'].search([('bsd_du_an_id', '=', self.bsd_du_an_id.id),
                                                     ('bsd_nvbh_id', '=', self.bsd_nvbh_id.id),
                                                     ('bsd_unit_id', '=', self.bsd_unit_id.id),
                                                     ('state', 'in', ['nhap', 'giu_cho', 'dat_cho'])])
        if len(gc_in_unit) > self.bsd_du_an_id.bsd_gc_unit_nv:
            raise UserError("Tổng số giữ chỗ trên Sản phẩm của bạn đã vượt quá quy định!")

    # KD.07.03 Ràng buộc số giữ chỗ theo Sản phẩm
    @api.constrains('bsd_unit_id')
    def _constrain_unit(self):

        gc_in_unit = self.env['bsd.giu_cho'].search([('bsd_du_an_id', '=', self.bsd_du_an_id.id),
                                                     ('bsd_unit_id', '=', self.bsd_unit_id.id),
                                                     ('state', 'in', ['nhap', 'giu_cho', 'dat_cho'])])
        if len(gc_in_unit) > self.bsd_du_an_id.bsd_gc_unit:
            raise UserError("Tổng số giữ chỗ trên Sản phẩm đã vượt quá quy định!")

    # KD.07.04 Ràng buộc số giữ chỗ theo NVBH/ngày
    @api.constrains('bsd_nvbh_id', 'bsd_ngay_gc')
    def _constrain_nv_bh(self):
        min_time = datetime.datetime.combine(datetime.date.today(), datetime.datetime.min.time())
        max_time = datetime.datetime.combine(datetime.date.today(), datetime.datetime.max.time())
        gc_in_day = self.env['bsd.giu_cho'].search([('bsd_ngay_gc', '<', max_time),
                                                   ('bsd_ngay_gc', '>', min_time),
                                                   ('bsd_du_an_id', '=', self.bsd_du_an_id.id),
                                                   ('bsd_nvbh_id', '=', self.bsd_nvbh_id.id),
                                                   ('state', 'in', ['nhap', 'giu_cho', 'dat_cho'])])
        if len(gc_in_day) > self.bsd_du_an_id.bsd_gc_nv_ngay:
            raise UserError("Tổng số Giữ chỗ trên một ngày của bạn đã vượt quá quy định")

    # KD.07.05 Ràng buộc số giữ chỗ theo Sản phẩm/NVBH/ngày
    @api.constrains('bsd_nvbh_id', 'bsd_unit_id', 'bsd_ngay_gc')
    def _constrain_unit_nv_ngay(self):
        min_time = datetime.datetime.combine(datetime.date.today(), datetime.datetime.min.time())
        max_time = datetime.datetime.combine(datetime.date.today(), datetime.datetime.max.time())
        gc_in_day = self.env['bsd.giu_cho'].search([('bsd_ngay_gc', '<', max_time),
                                                   ('bsd_ngay_gc', '>', min_time),
                                                   ('bsd_du_an_id', '=', self.bsd_du_an_id.id),
                                                   ('bsd_unit_id', '=', self.bsd_unit_id.id),
                                                   ('bsd_nvbh_id', '=', self.bsd_nvbh_id.id),
                                                   ('state', 'in', ['nhap', 'giu_cho', 'dat_cho'])])
        if len(gc_in_day) > self.bsd_du_an_id.bsd_gc_unit_nv_ngay:
            raise UserError("Tổng số Giữ chỗ trong ngày theo Sản phẩm của bạn đã vượt quá quy định")

    @api.onchange('bsd_unit_id', 'bsd_du_an_id')
    def _onchange_tien_gc(self):
        if self.bsd_unit_id:
            self.bsd_dot_mb_id = self.bsd_unit_id.bsd_dot_mb_id
            tien_gc = self.bsd_unit_id.bsd_tien_gc
            if tien_gc != 0:
                self.bsd_tien_gc = tien_gc
            else:
                self.bsd_tien_gc = self.bsd_du_an_id.bsd_tien_gc

        if self.bsd_dot_mb_id:
            self.bsd_tien_gc = 0

    # R.05 Tính hạn hiệu lực giữ chỗ
    @api.depends('bsd_ngay_gc', 'bsd_du_an_id.bsd_gc_smb')
    def _compute_hl_gc(self):
        for each in self:
            if each.bsd_ngay_gc:
                hours = each.bsd_du_an_id.bsd_gc_smb or 0 if each.bsd_du_an_id else 0
                each.bsd_ngay_hh_gc = each.bsd_ngay_gc + datetime.timedelta(hours=hours)

    # R.08 Tính hạn hiệu lực giữ chỗ sau thanh toán
    @api.depends('bsd_ngay_tt', 'bsd_du_an_id.bsd_gc_tmb')
    def _compute_ngay_hh_stt(self):
        for each in self:
            if each.bsd_ngay_tt:
                each.bsd_ngay_hh_stt = each.bsd_ngay_tt + datetime.timedelta(days=each.bsd_du_an_id.bsd_gc_tmb)

    # KD.07.09 Theo dõi công nợ giữ chỗ
    def _tao_rec_cong_no(self):
        if self.bsd_truoc_mb and not self.bsd_gc_da:
            self.env['bsd.cong_no'].create({
                'bsd_chung_tu': self.bsd_ma_gc,
                'bsd_ngay': self.bsd_ngay_gc,
                'bsd_khach_hang_id': self.bsd_khach_hang_id.id,
                'bsd_du_an_id': self.bsd_du_an_id.id,
                'bsd_ps_tang': self.bsd_tien_gc,
                'bsd_ps_giam': 0,
                'bsd_loai_ct': 'giu_cho',
                'bsd_phat_sinh': 'tang',
                'bsd_giu_cho_id': self.id,
                'state': 'da_gs',
            })

    # KD07.01 Xác nhận giữ chỗ
    def action_xac_nhan(self):
        if not self.bsd_dot_mb_id:
            self._tao_rec_cong_no()
            self.write({
                'state': 'dat_cho',
                'bsd_ngay_gc': datetime.datetime.now(),
            })
            # Cập nhật lại trạng thái unit
            if self.bsd_unit_id.state in ['giu_cho', 'dat_cho']:
                pass
            else:
                self.bsd_unit_id.write({
                    'state': 'dat_cho',
                })
        else:
            giu_cho_unit = self.env['bsd.giu_cho'].search([('bsd_unit_id', '=', self.bsd_unit_id.id),
                                                           ('bsd_stt_bg', '>', 0)])
            stt = 1
            time_gc = self.bsd_du_an_id.bsd_gc_smb
            ngay_hh_bg = datetime.datetime.now() + datetime.timedelta(hours=time_gc)
            if giu_cho_unit:
                stt = max(filter(None, giu_cho_unit.mapped('bsd_stt_bg'))) + 1
                ngay_hh_bg = max(filter(None, giu_cho_unit.mapped('bsd_ngay_hh_bg'))) + datetime.timedelta(hours=time_gc)
            self.write({
                'state': 'giu_cho',
                'bsd_ngay_gc': datetime.datetime.now(),
                'bsd_stt_bg': stt,
                'bsd_ngay_hh_bg': ngay_hh_bg,
            })
            # Cập nhật lại trạng thái unit
            self.bsd_unit_id.write({
                'state': 'giu_cho',
            })

    # KD.07.07 Tự động hủy giữ chỗ quá hạn thanh toán
    def auto_huy_gc(self):
        self.write({
            'state': 'huy',
        })

    # KD.07.08 Tự động đánh dấu hết hạn giữ chỗ
    def auto_danh_dau_hh_gc(self):
        self.write({
            'bsd_het_han_gc': True
        })

    # R7 Ghi nhận thông tin trước mở bán
    @api.model
    def create(self, vals):
        sequence = False
        if 'bsd_du_an_id' in vals:
            du_an = self.env['bsd.du_an'].browse(vals['bsd_du_an_id'])
            sequence = du_an.get_ma_bo_cn(loai_cn=self._name)
        if not sequence:
            raise UserError(_('Dự án chưa có mã phiếu giữ chỗ'))
        vals['bsd_ma_gc'] = sequence.next_by_id()
        res = super(BsdGiuCho, self).create(vals)
        if res.bsd_unit_id.bsd_dot_mb_id:
            res.write({
                'bsd_truoc_mb': False,
            })
        else:
            res.write({
                'bsd_truoc_mb': True,
            })
        # R11 Chuyển nhượng khách hàng
        res.write({
            'bsd_kh_moi_id': res.bsd_khach_hang_id.id
        })
        return res

    def write(self, vals):
        if 'bsd_unit_id' in vals:
            if self.env['product.product'].browse(vals['bsd_unit_id']).bsd_dot_mb_id:
                vals.update({
                    'bsd_truoc_mb': False,
                })
            else:
                vals.update({
                    'bsd_truoc_mb': True,
                })
            _logger.debug(vals)
        if 'bsd_khach_hang_id' in vals:
            vals.update({
                'bsd_kh_moi_id': vals['bsd_khach_hang_id']
            })
        res = super(BsdGiuCho, self).write(vals)
        return res

    # KD.07.06 Hủy giữ chỗ đã thanh toán
    def action_huy(self):
        # Kiểm tra giữ chỗ đã làm báo giá chưa
        bao_gia = self.env['bsd.bao_gia'].search([('bsd_giu_cho_id', '=', self.id),
                                                  ('state', 'not in', ['huy'])])
        if bao_gia:
            raise UserError("Bạn cần hủy Bảng tính giá trước khi hủy giữ chỗ")

        # Hủy giữ chỗ sau mở bán
        if self.bsd_thanh_toan == 'da_tt' and not self.bsd_truoc_mb:
            self.write({'state': 'huy'})
            giu_cho = self.env['bsd.giu_cho'].search([('bsd_unit_id', '=', self.bsd_unit_id.id),
                                                      ('state', 'not in', ['huy', 'nhap'])])
            if not giu_cho:
                self.bsd_unit_id.write({
                    'state': 'san_sang',
                })
            elif not giu_cho.filtered(lambda g: g.state == 'giu_cho'):
                self.bsd_unit_id.write({
                    'state': 'dat_cho'
                })
        # Hủy giữ chỗ từ giữ chỗ thiện chí
        if self.bsd_thanh_toan == 'da_tt' and self.bsd_gc_da:
            # Hủy giữ chỗ và ráp căn của giữ chỗ
            self.write({'state': 'huy'})
            self.bsd_rap_can_id.write({'state': 'huy'})
            giu_cho = self.env['bsd.giu_cho'].search([('bsd_unit_id', '=', self.bsd_unit_id.id),
                                                      ('state', 'not in', ['huy', 'nhap'])])
            if not self.bsd_dot_mb_id:
                if not giu_cho:
                    self.bsd_unit_id.write({
                        'state': 'chuan_bi',
                    })
                elif not giu_cho.filtered(lambda g: g.state == 'giu_cho'):
                    self.bsd_unit_id.write({
                        'state': 'dat_cho'
                    })
            else:
                if not giu_cho:
                    self.bsd_unit_id.write({
                        'state': 'san_sang',
                    })
                elif not giu_cho.filtered(lambda g: g.state == 'giu_cho'):
                    self.bsd_unit_id.write({
                        'state': 'dat_cho'
                    })

    # KD.07.06 Hủy giữ chỗ chưa thanh toán
    def action_huy_chua_tt(self):
        # cập nhật trạng thái giữ chỗ
        self.write({
            'state': 'huy',
        })
        self.env['bsd.cong_no'].search([('bsd_giu_cho_id', '=', self.id)], limit=1).write({
            'state': 'huy'
        })
        # cập nhật Sản phẩm trên phiếu giữ chỗ
        if not self.bsd_dot_mb_id:
            giu_cho = self.env['bsd.giu_cho'].search([('bsd_unit_id', '=', self.bsd_unit_id.id),
                                                      ('state', 'not in', ['huy', 'nhap'])])
            if not giu_cho:
                self.bsd_unit_id.write({
                    'state': 'chuan_bi',
                })
        else:
            giu_cho = self.env['bsd.giu_cho'].search([('bsd_unit_id', '=', self.bsd_unit_id.id),
                                                      ('state', 'not in', ['huy', 'nhap'])])
            if not giu_cho:
                self.bsd_unit_id.write({
                    'state': 'san_sang',
                })

    # KD.07.10 Tự động tính Hạn báo giá của Giữ chỗ thanh toán sau mở bán
    def tinh_lai_hbg(self):
        if not self.bsd_dot_mb_id:
            pass
        else:
            pass

    # KD.07.11 Tạo Bảng tính giá từ màn hình Giữ chỗ
    def action_tao_bao_gia(self):
        context = {
            'default_bsd_ten_bao_gia': 'Bảng tính giá sản phẩm ' + self.bsd_unit_id.name,
            'default_bsd_khach_hang_id': self.bsd_khach_hang_id.id,
            'default_bsd_giu_cho_id': self.id,
            'default_bsd_nvbh_id': self.bsd_nvbh_id.id,
            'default_bsd_san_gd_id': self.bsd_san_gd_id.id,
            'default_bsd_ctv_id': self.bsd_ctv_id.id,
            'default_bsd_gioi_thieu_id': self.bsd_gioi_thieu_id.id,
            'default_state': 'nhap',
        }
        action = self.env.ref('bsd_kinh_doanh.bsd_bao_gia_action_popup').read()[0]
        action['context'] = context
        return action
        # return {
        #     "name": "Tạo bảng tính giá",
        #     "res_model": 'bsd.bao_gia',
        #     "view": [[False, 'form']],
        #     "type": 'ir.actions.act_window',
        #     "view_mode": "form",
        #     "context": context,
        #     "target": "new"
        # }

    def _compute_bao_gia(self):
        for each in self:
            bao_gia = self.env['bsd.bao_gia'].search([('bsd_giu_cho_id', '=', self.id)])
            each.bsd_so_bao_gia = len(bao_gia)

    def _compute_huy_gc(self):
        for each in self:
            huy_gc = self.env['bsd.huy_gc'].search([('bsd_giu_cho_id', '=', self.id)])
            each.bsd_so_huy_gc = len(huy_gc)

    def action_view_bao_gia(self):
        action = self.env.ref('bsd_kinh_doanh.bsd_bao_gia_action').read()[0]

        bao_gia = self.env['bsd.bao_gia'].search([('bsd_giu_cho_id', '=', self.id)])
        if len(bao_gia) > 1:
            action['domain'] = [('id', 'in', bao_gia.ids)]
        elif bao_gia:
            form_view = [(self.env.ref('bsd_kinh_doanh.bsd_bao_gia_form').id, 'form')]
            if 'views' in action:
                action['views'] = form_view + [(state, view) for state, view in action['views'] if view != 'form']
            else:
                action['views'] = form_view
            action['res_id'] = bao_gia.id
        # Prepare the context.
        context = {
            'default_bsd_ten_bao_gia': 'Bảng tính giá Sản phẩm' + self.bsd_unit_id.name,
            'default_bsd_khach_hang_id': self.bsd_kh_moi_id.id,
            'default_bsd_giu_cho_id': self.id,
            'default_bsd_nvbh_id': self.bsd_nvbh_id.id,
            'default_bsd_san_gd_id': self.bsd_san_gd_id.id,
            'default_bsd_ctv_id': self.bsd_ctv_id.id,
            'default_bsd_gioi_thieu_id': self.bsd_gioi_thieu_id.id,
        }
        action['context'] = context
        return action

    def action_view_huy_gc(self):
        action = self.env.ref('bsd_kinh_doanh.bsd_huy_gc_action').read()[0]

        huy_gc = self.env['bsd.huy_gc'].search([('bsd_giu_cho_id', '=', self.id)])
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
            'default_bsd_khach_hang_id': self.bsd_kh_moi_id.id,
            'default_bsd_giu_cho_id': self.id,
            'default_bsd_du_an_id': self.bsd_du_an_id.id,
            'default_bsd_loai_gc': 'giu_cho'
        }
        action['context'] = context
        return action

    # KD.07.13 Tạo đề nghị hủy giữ chỗ từ màn hình Giữ chỗ
    def action_de_nghi_huy(self):
        context = {
            'default_bsd_khach_hang_id': self.bsd_kh_moi_id.id,
            'default_bsd_giu_cho_id': self.id,
            'default_bsd_du_an_id': self.bsd_du_an_id.id,
            'default_bsd_loai_gc': 'giu_cho',
            'default_bsd_unit_id': self.bsd_unit_id.id,
        }
        return {
            "name": "Tạo đề nghị hủy",
            "res_model": 'bsd.huy_gc',
            "view": [[False, 'form']],
            "type": 'ir.actions.act_window',
            "view_mode": "form",
            "context": context,
            "target": "new"
        }