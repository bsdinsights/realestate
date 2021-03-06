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
                                    readonly=True, states={'nhap': [('readonly', False)]})

    bsd_bang_gia_id = fields.Many2one('product.pricelist', related="bsd_dot_mb_id.bsd_bang_gia_id", store=True,
                                      string="Bảng giá", help="Bảng giá bán")
    bsd_tien_gc = fields.Monetary(string="Tiền giữ chỗ", required=True,
                                  readonly=True, help="Tiền giữ chỗ",
                                  states={'nhap': [('readonly', False)]})

    def _get_nhan_vien(self):
        return self.env['hr.employee'].search([('user_id', '=', self.env.uid)])

    bsd_nvbh_id = fields.Many2one('hr.employee', string="Nhân viên KD", help="Nhân viên kinh doanh",
                                  readonly=True, required=True, default=_get_nhan_vien,
                                  states={'nhap': [('readonly', False)]})
    bsd_san_gd_id = fields.Many2one('res.partner', string="Sàn giao dịch", domain=[('is_company', '=', True)],
                                    readonly=True, help="Sàn giao dịch",
                                    states={'nhap': [('readonly', False)]})
    bsd_ctv_id = fields.Many2one('res.partner', string="Cộng tác viên", domain=[('is_company', '=', False)],
                                 readonly=True, help="Cộng tác viên",
                                 states={'nhap': [('readonly', False)]})
    bsd_gioi_thieu_id = fields.Many2one('res.partner', string="Giới thiệu", help="Cá nhân hoặc đơn vị giới thiệu",
                                        readonly=True,
                                        states={'nhap': [('readonly', False)]})
    bsd_ngay_hh_gc = fields.Datetime(string="Hạn giữ chỗ", help="Hiệu lực của giữ chỗ", tracking=3)

    bsd_gc_da = fields.Boolean(string="Giữ chỗ dự án", help="""Thông tin ghi nhận Giữ chỗ được tự động tạo từ 
                                                                giữ chỗ thiện chí hay không""", readonly=True)
    bsd_gc_tc_id = fields.Many2one('bsd.gc_tc', string="Giữ chỗ thiện chí", readonly=True,
                                   help="Phiếu giữ chỗ thiện chí",)
    bsd_rap_can_id = fields.Many2one('bsd.rap_can', string="Ráp căn", help="Phiếu ráp căn", readonly=True)
    state = fields.Selection([('nhap', 'Nháp'),
                              ('dat_cho', 'Đặt chỗ'),
                              ('dang_cho', "Đang chờ"),
                              ('giu_cho', 'Giữ chỗ'),
                              ('hoan_thanh', 'Hoàn thành'),
                              ('het_han', 'Hết hạn'),
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
    bsd_stt_bg = fields.Integer(string="Số ưu tiên", readonly=True, help="Số ưu tiên giữ chỗ")
    bsd_ngay_hh_bg = fields.Datetime(string="Ngày ưu tiên", help="Ưu tiên làm bảng tính giá", readonly=True)
    bsd_het_han_gc = fields.Boolean(string="Hết hạn giữ chỗ", readonly=True,
                                    help="""Thông tin ghi nhận giữ chỗ bị hết hiệu lực sau khi đã thanh toán giữ chỗ""")

    bsd_kh_moi_id = fields.Many2one('res.partner', string="KH đứng tên", help="Người được chuyển tên giữ chỗ",
                                    tracking=2, readonly=True)

    bsd_tien_gctc = fields.Monetary(string="Tiền GCTC", help="Tiền giữ chỗ thiện chí đã thanh toán",
                                    readonly=True, default=0)
    bsd_huy_gc_id = fields.Many2one('bsd.huy_gc', string="Hủy giữ chỗ", help="Mã phiếu hủy giữ chỗ", readonly=1)

    bsd_so_bao_gia = fields.Integer(string="# Bảng tính giá", compute='_compute_bao_gia')
    bsd_so_huy_gc = fields.Integer(string="# Hủy giữ chỗ", compute='_compute_huy_gc')
    bsd_so_chuyen_gc = fields.Integer(string="# Chuyển GC", compute='_compute_chuyen_gc')
    bsd_so_gia_han = fields.Integer(string="# Gia hạn", compute='_compute_gia_han')
    bsd_so_chuyen_ut_gc = fields.Integer(string="# Chuyển UT", compute='_compute_chuyen_ut_gc')

    # tiện ích chuyển độ ưu tiên
    def action_chuyen_ut_gc(self):
        context = {
            'default_bsd_giu_cho_ch_id': self.id,
            'default_bsd_du_an_id': self.bsd_du_an_id.id,
            'default_bsd_loai_gc': 'giu_cho',
            'default_bsd_unit_id': self.bsd_unit_id.id
        }
        action = self.env.ref('bsd_kinh_doanh.bsd_chuyen_ut_gc_action_popup').read()[0]
        action['context'] = context
        return action

    def _compute_chuyen_ut_gc(self):
        for each in self:
            chuyen_ut_gc = self.env['bsd.chuyen_ut_gc'].search([('bsd_giu_cho_ch_id', '=', self.id)])
            each.bsd_so_chuyen_ut_gc = len(chuyen_ut_gc)

    def action_view_chuyen_ut_gc(self):
        action = self.env.ref('bsd_kinh_doanh.bsd_chuyen_ut_gc_action').read()[0]

        chuyen_gc = self.env['bsd.chuyen_ut_gc'].search([('bsd_giu_cho_ch_id', '=', self.id)])
        if len(chuyen_gc) > 1:
            action['domain'] = [('id', 'in', chuyen_gc.ids)]
        elif chuyen_gc:
            form_view = [(self.env.ref('bsd_kinh_doanh.bsd_chuyen_ut_gc_form').id, 'form')]
            if 'views' in action:
                action['views'] = form_view + [(state, view) for state, view in action['views'] if view != 'form']
            else:
                action['views'] = form_view
            action['res_id'] = chuyen_gc.id
        return action

    def _compute_gia_han(self):
        for each in self:
            gia_han = self.env['bsd.gia_han_gc_ct'].search([('bsd_giu_cho_id', '=', self.id),
                                                           ('state', '=', 'hieu_luc')])
            each.bsd_so_gia_han = len(gia_han)

    def action_view_gia_han(self):
        action = self.env.ref('bsd_kinh_doanh.bsd_gia_han_gc_ct_action').read()[0]

        gia_han = self.env['bsd.gia_han_gc_ct'].search([('bsd_giu_cho_id', '=', self.id),
                                                       ('state', '=', 'hieu_luc')])
        action['domain'] = [('id', 'in', gia_han.ids)]
        return action

    # 3 field ctv , sàn gd, giới thiệu không tồn tại đồng thời
    # Khách hàng không được trùng với mô giới
    @api.constrains('bsd_ctv_id', 'bsd_san_gd_id', 'bsd_gioi_thieu_id', 'bsd_khach_hang_id')
    def _constrains_mo_gioi(self):
        if (self.bsd_ctv_id and self.bsd_san_gd_id) \
            or (self.bsd_ctv_id and self.bsd_gioi_thieu_id) \
               or (self.bsd_san_gd_id and self.bsd_gioi_thieu_id):
            raise UserError("Vui lòng chọn 1 trong 3 giá trị: Sàn giao dịch, Công tác viên, Khách hàng giới thiệu.")
        if self.bsd_khach_hang_id == self.bsd_ctv_id \
            or self.bsd_khach_hang_id == self.bsd_san_gd_id \
                or self.bsd_khach_hang_id == self.bsd_gioi_thieu_id:
            raise UserError("Thông tin môi giới không được trùng với khách hàng.\nVui lòng kiểm tra lại thông tin.")

    @api.onchange('bsd_nvbh_id')
    def _onchange_san_ctv(self):
        res = {}
        self.env.cr.execute("""SELECT bsd_cn_id FROM bsd_loai_cn_rel 
                                WHERE bsd_loai_id = {0}
                            """.format(self.env.ref('bsd_kinh_doanh.bsd_ctv').id))
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

    # Tên hiện thị record
    def name_get(self):
        res = []
        for gc in self:
            res.append((gc.id, "{0} - {1}".format(gc.bsd_ma_gc, gc.bsd_ten_sp)))
        return res
    
    @api.model
    def _name_search(self, name='', args=None, operator='ilike', limit=100, name_get_uid=None):
        args = list(args or [])
        if name:
            if operator == 'ilike':
                args += [('bsd_ten_sp', operator, name)]
            elif operator == '=':
                args += [('bsd_ma_gc', operator, name)]
        access_rights_uid = name_get_uid or self._uid
        ids = self._search(args, limit=limit, access_rights_uid=access_rights_uid)
        recs = self.browse(ids)
        return models.lazy_name_get(recs.with_user(access_rights_uid))

    @api.constrains('bsd_tien_gc')
    def _check_bsd_tien_gc(self):
        for record in self:
            if record.bsd_tien_gc < 0:
                raise ValidationError("Tiền giữ chỗ phải lớn hơn 0.")

    # Kiểm tra căn hộ có đang ưu tiên hay ko
    @api.constrains('bsd_unit_id')
    def _constraint_unit_ut(self):
        if self.bsd_unit_id.bsd_uu_tien == '1':
            raise UserError(_("""Sản phẩm {0} đang được ưu tiên.\nVui lòng chọn sản phẩm khác để giao dịch.""".format(self.bsd_unit_id.bsd_ma_unit)))

    # KD.07.02 Ràng buộc số giữ chỗ theo Sản phẩm/ NVKD
    @api.constrains('bsd_nvbh_id', 'bsd_unit_id')
    def _constrain_unit_nv(self):
        _logger.debug("Ràng buộc số giữ chỗ theo Sản phẩm/ NVBH.")
        if self.bsd_du_an_id.bsd_gc_unit_nv:
            gc_in_unit = self.env['bsd.giu_cho'].search([('bsd_du_an_id', '=', self.bsd_du_an_id.id),
                                                         ('bsd_nvbh_id', '=', self.bsd_nvbh_id.id),
                                                         ('bsd_thanh_toan', '!=', 'chua_tt'),
                                                         ('state', 'in', ['dat_cho', 'giu_cho', 'dang_cho'])])
            gc_in_unit += self
            unit = gc_in_unit.mapped('bsd_unit_id')
            _logger.debug(unit)
            if len(unit) > self.bsd_du_an_id.bsd_gc_unit_nv:
                raise UserError("Tổng số sản phẩm bạn thực hiện giữ chỗ đã vượt quá quy định dự án!")

    # Kiểm tra khách hàng đã giữ chỗ căn hộ này chưa
    @api.constrains('bsd_unit_id', 'bsd_khach_hang_id')
    def _constrain_kh(self):
        gc_kh = self.env['bsd.giu_cho'].search([('bsd_unit_id', '=', self.bsd_unit_id.id),
                                                ('id', '!=', self.id),
                                                ('bsd_khach_hang_id', '=', self.bsd_khach_hang_id.id),
                                                ('state', 'not in', ['huy', 'het_han', 'dong'])])
        if gc_kh:
            raise UserError(_("Khách hàng đã tạo giữ chỗ sản phẩm này.\nVui lòng kiểm tra lại thông tin."))

    # Kiểm tra sản phẩm có thuộc dự án đã chọn hay ko
    # Kiểm tra dự án đã phát hành hay chưa
    @api.constrains('bsd_unit_id', 'bsd_du_an_id')
    def _constrain_da(self):
        if self.bsd_unit_id.bsd_du_an_id != self.bsd_du_an_id:
            raise UserError(_("Sản phẩm không nằm trong dự án.\nVui lòng kiểm tra lại thông tin."))
        if self.bsd_du_an_id.state != 'phat_hanh':
            raise UserError(_("Dự án chưa ban hành.\nVui lòng kiểm tra lại thông tin."))

    @api.onchange('bsd_ngay_gc', 'bsd_du_an_id',)
    def _onchange_ngay_gc(self):
        self.bsd_ngay_hh_gc = self.bsd_ngay_gc + datetime.timedelta(days=self.bsd_du_an_id.bsd_gc_tmb)

    # KD.07.03 Ràng buộc số giữ chỗ theo Sản phẩm
    @api.constrains('bsd_unit_id')
    def _constrain_unit(self):
        if self.bsd_du_an_id.bsd_gc_unit:
            gc_in_unit = self.env['bsd.giu_cho'].search([('bsd_du_an_id', '=', self.bsd_du_an_id.id),
                                                         ('bsd_unit_id', '=', self.bsd_unit_id.id),
                                                         ('state', 'in', ['giu_cho', 'dang_cho'])])
            gc_in_unit += self
            if len(gc_in_unit) > self.bsd_du_an_id.bsd_gc_unit:
                raise UserError("Tổng số giữ chỗ trên Sản phẩm đã vượt quá quy định!")

    # KD.07.04 Ràng buộc số giữ chỗ theo NVBH/ngày
    @api.constrains('bsd_nvbh_id', 'bsd_ngay_gc')
    def _constrain_nv_bh(self):
        if self.bsd_du_an_id.bsd_gc_nv_ngay:
            min_time = datetime.datetime.combine(datetime.date.today(), datetime.datetime.min.time())
            max_time = datetime.datetime.combine(datetime.date.today(), datetime.datetime.max.time())
            gc_in_day = self.env['bsd.giu_cho'].search([('bsd_ngay_gc', '<', max_time),
                                                       ('bsd_ngay_gc', '>', min_time),
                                                       ('bsd_du_an_id', '=', self.bsd_du_an_id.id),
                                                       ('bsd_nvbh_id', '=', self.bsd_nvbh_id.id),
                                                       ('bsd_thanh_toan', '!=', 'chua_tt'),
                                                       ('state', 'in', ['dat_cho', 'giu_cho', 'dang_cho'])])
            gc_in_day += self
            if len(gc_in_day) > self.bsd_du_an_id.bsd_gc_nv_ngay:
                raise UserError("Tổng số Giữ chỗ trên một ngày của bạn đã vượt quá quy định.")

    # KD.07.05 Ràng buộc số giữ chỗ theo Sản phẩm/NVBH/ngày
    @api.constrains('bsd_nvbh_id', 'bsd_unit_id', 'bsd_ngay_gc')
    def _constrain_unit_nv_ngay(self):
        if self.bsd_du_an_id.bsd_gc_unit_nv_ngay:
            min_time = datetime.datetime.combine(datetime.date.today(), datetime.datetime.min.time())
            max_time = datetime.datetime.combine(datetime.date.today(), datetime.datetime.max.time())
            gc_in_day = self.env['bsd.giu_cho'].search([('bsd_ngay_gc', '<', max_time),
                                                       ('bsd_ngay_gc', '>', min_time),
                                                       ('bsd_du_an_id', '=', self.bsd_du_an_id.id),
                                                       ('bsd_nvbh_id', '=', self.bsd_nvbh_id.id),
                                                       ('state', 'in', ['giu_cho', 'dang_cho'])])
            gc_in_day += self
            unit = gc_in_day.mapped('bsd_unit_id')
            if len(unit) > self.bsd_du_an_id.bsd_gc_unit_nv_ngay:
                raise UserError("Tổng số Giữ chỗ trong ngày theo Sản phẩm của bạn đã vượt quá quy định.")

    # Kiểm tra trạng thái unit trước khi tạo giữ chỗ
    @api.constrains('bsd_unit_id')
    def _constrains_state_giu_cho(self):
        if self.bsd_unit_id.state not in ['chuan_bi', 'san_sang', 'dat_cho', 'giu_cho']:
            raise UserError(_("Sản phẩm đã có giao dịch.\nVui lòng kiểm tra lại thông tin sản phẩm."))

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
        if self.bsd_du_an_id.state != 'phat_hanh':
            raise UserError(_("Dự án đang ở giai đoạn chuẩn bị, không thể xác nhận giữ chỗ."
                              "\nVui lòng kiểm tra lại thông tin."))
        if not self.bsd_dot_mb_id:
            self._tao_rec_cong_no()
            now = datetime.datetime.now()
            self.bsd_ngay_hh_gc = self.bsd_ngay_gc + datetime.timedelta(hours=self.bsd_du_an_id.bsd_gc_smb)
            self.write({
                'state': 'dat_cho',
                'bsd_ngay_gc': now,
                'bsd_ngay_hh_gc': now + datetime.timedelta(hours=self.bsd_du_an_id.bsd_gc_smb)

            })
            # Cập nhật lại trạng thái unit
            if self.bsd_unit_id.state in ['giu_cho', 'dat_cho']:
                pass
            else:
                self.bsd_unit_id.sudo().write({
                    'state': 'dat_cho',
                })
        # Khi đã có đợt mở bán xem sản phẩm đã có đặt cọc chưa
        else:
            if self.bsd_unit_id.state not in ['chuan_bi', 'san_sang', 'dat_cho', 'giu_cho']:
                raise UserError(_("Sản phẩm đã có giao dịch.\nVui lòng kiểm tra lại thông tin."))
            giu_cho_unit = self.env['bsd.giu_cho'].search([('bsd_unit_id', '=', self.bsd_unit_id.id),
                                                           ('state', '=', 'giu_cho')])
            time_gc = self.bsd_du_an_id.bsd_gc_smb
            ngay_hh_bg = fields.Datetime.now()
            ngay_hh_gc = ngay_hh_bg + datetime.timedelta(hours=time_gc)
            stt = self.bsd_unit_id.bsd_sequence_gc_id.next_by_id()
            if giu_cho_unit:
                self.write({
                    'bsd_ngay_hh_bg': ngay_hh_bg,
                    'bsd_ngay_hh_gc': ngay_hh_gc,
                    'state': 'dang_cho',
                    'bsd_stt_bg': stt
                })
            else:
                self.write({
                    'bsd_ngay_hh_bg': ngay_hh_bg,
                    'bsd_ngay_hh_gc': ngay_hh_gc,
                    'state': 'giu_cho',
                    'bsd_stt_bg': stt
                })
            # Cập nhật lại trạng thái unit
            self.bsd_unit_id.sudo().write({
                'state': 'giu_cho',
            })

    # KD.07.07 Tự động hủy giữ chỗ quá hạn thanh toán
    # KD.07.08 Tự động đánh dấu hết hạn giữ chỗ
    def auto_huy_gc(self):
        if self.bsd_thanh_toan == 'chua_tt' and self.bsd_truoc_mb:
            self.write({
                'state': 'het_han'
            })
            # Cập nhật trạng thái unit
            giu_cho = self.env['bsd.giu_cho'].search([('bsd_unit_id', '=', self.bsd_unit_id.id),
                                                      ('state', 'in', ['dat_cho', 'dang_cho', 'giu_cho']),
                                                      ('id', '!=', self.id)])
            if not self.bsd_unit_id.bsd_dot_mb_id:
                if not giu_cho:
                    self.bsd_unit_id.sudo().write({
                        'state': 'chuan_bi',
                    })
                elif not giu_cho.filtered(lambda g: g.state in ['dang_cho', 'giu_cho']):
                    self.bsd_unit_id.sudo().write({
                        'state': 'dat_cho'
                    })
            else:
                if not giu_cho:
                    self.bsd_unit_id.sudo().write({
                        'state': 'san_sang',
                    })
                elif not giu_cho.filtered(lambda g: g.state in ['dang_cho', 'giu_cho']):
                    self.bsd_unit_id.sudo().write({
                        'state': 'dat_cho'
                    })
        elif not self.bsd_truoc_mb:
            if self.state == 'giu_cho':
                self.write({
                    'state': 'het_han'
                })
                # Kiểm tra ngày ưu tiên báo giá nhỏ nhất
                self.env.cr.execute("""SELECT MIN(bsd_ngay_hh_bg) FROM bsd_giu_cho
                                        WHERE bsd_unit_id = {0} AND state = 'dang_cho'
                                    """.format(self.bsd_unit_id.id))
                min_ngay_ut = self.env.cr.fetchone()[0]
                if min_ngay_ut:
                    # lấy số thứ tự giữ chỗ thiện chí tiếp theo đang ở trạng thái chờ
                    next_giu_cho = self.env['bsd.giu_cho'].search([('bsd_ngay_hh_bg', '=', min_ngay_ut)])
                    _logger.debug(next_giu_cho)
                    next_giu_cho.write({
                        'state': 'giu_cho'
                    })
            else:
                self.write({
                    'state': 'het_han'
                })
            # Cập nhật trạng thái unit
            giu_cho = self.env['bsd.giu_cho'].search([('bsd_unit_id', '=', self.bsd_unit_id.id),
                                                      ('state', 'in', ['dat_cho', 'dang_cho', 'giu_cho']),
                                                      ('id', '!=', self.id)])
            if not self.bsd_unit_id.bsd_dot_mb_id:
                if not giu_cho:
                    self.bsd_unit_id.sudo().write({
                        'state': 'chuan_bi',
                    })
                elif not giu_cho.filtered(lambda g: g.state in ['dang_cho', 'giu_cho']):
                    self.bsd_unit_id.sudo().write({
                        'state': 'dat_cho'
                    })
            else:
                if not giu_cho:
                    self.bsd_unit_id.sudo().write({
                        'state': 'san_sang',
                    })
                elif not giu_cho.filtered(lambda g: g.state in ['dang_cho', 'giu_cho']):
                    self.bsd_unit_id.sudo().write({
                        'state': 'dat_cho'
                    })
        else:
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
            raise UserError(_('Dự án chưa có mã phiếu giữ chỗ.'))
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
        # import
        # res.action_xac_nhan()
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
            if self.state == 'giu_cho':
                self.write({'state': 'huy'})
                # Kiểm tra ngày ưu tiên báo giá nhỏ nhất
                self.env.cr.execute("""SELECT MIN(bsd_ngay_hh_bg) FROM bsd_giu_cho
                                        WHERE bsd_unit_id = {0} AND state = 'dang_cho'
                                    """.format(self.bsd_unit_id.id))
                min_ngay_ut = self.env.cr.fetchone()[0]
                if min_ngay_ut:
                    # lấy số thứ tự giữ chỗ thiện chí tiếp theo đang ở trạng thái chờ
                    next_giu_cho = self.env['bsd.giu_cho'].search([('bsd_ngay_hh_bg', '=', min_ngay_ut)])
                    _logger.debug(next_giu_cho)
                    next_giu_cho.write({
                        'state': 'giu_cho'
                    })
            else:
                self.write({'state': 'huy'})

            giu_cho = self.env['bsd.giu_cho'].search([('bsd_unit_id', '=', self.bsd_unit_id.id),
                                                      ('state', 'in', ['dat_cho', 'dang_cho', 'giu_cho'])])
            if not giu_cho:
                self.bsd_unit_id.sudo().write({
                    'state': 'san_sang',
                })
            elif not giu_cho.filtered(lambda g: g.state in ['dang_cho', 'giu_cho']):
                self.bsd_unit_id.sudo().write({
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
                                                      ('state', 'in', ['dat_cho', 'dang_cho', 'giu_cho'])])
            if not giu_cho:
                self.bsd_unit_id.sudo().write({
                    'state': 'chuan_bi',
                })
        else:
            giu_cho = self.env['bsd.giu_cho'].search([('bsd_unit_id', '=', self.bsd_unit_id.id),
                                                      ('state', 'in', ['dat_cho', 'dang_cho', 'giu_cho'])])
            if not giu_cho:
                self.bsd_unit_id.sudo().write({
                    'state': 'san_sang',
                })

    # KD.07.11 Tạo Bảng tính giá từ màn hình Giữ chỗ
    def action_tao_bao_gia(self):
        context = {
            'default_bsd_ten_bao_gia': 'Bảng tính giá sản phẩm ' + self.bsd_unit_id.name,
            'default_bsd_khach_hang_id': self.bsd_khach_hang_id.id,
            'default_bsd_du_an_id': self.bsd_du_an_id.id,
            'default_bsd_giu_cho_id': self.id,
            'default_bsd_unit_id': self.bsd_unit_id.id,
            'default_bsd_nvbh_id': self.bsd_nvbh_id.id,
            'default_bsd_san_gd_id': self.bsd_san_gd_id.id,
            'default_bsd_ctv_id': self.bsd_ctv_id.id,
            'default_bsd_gioi_thieu_id': self.bsd_gioi_thieu_id.id,
            'default_state': 'nhap',
        }
        action = self.env.ref('bsd_kinh_doanh.bsd_bao_gia_action_popup').read()[0]
        action['context'] = context
        return action

    # Nút nhấn in
    def action_in(self):
        return self.env.ref('bsd_kinh_doanh.bsd_giu_cho_report_action').read()[0]

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
        action = self.env.ref('bsd_kinh_doanh.bsd_huy_gc_action_popup_2').read()[0]
        action['context'] = context
        return action

    # tiện ích chuyển gc
    def action_chuyen_gc(self):
        context = {
            'default_bsd_kh_ht_id': self.bsd_kh_moi_id.id,
            'default_bsd_giu_cho_id': self.id,
            'default_bsd_unit_id': self.bsd_unit_id.id,
            'default_bsd_du_an_id': self.bsd_du_an_id.id,
            'default_bsd_loai_gc': 'giu_cho',
        }
        action = self.env.ref('bsd_kinh_doanh.bsd_chuyen_gc_action_popup').read()[0]
        action['context'] = context
        return action

    def _compute_chuyen_gc(self):
        for each in self:
            chuyen_gc = self.env['bsd.chuyen_gc'].search([('bsd_giu_cho_id', '=', self.id)])
            each.bsd_so_chuyen_gc = len(chuyen_gc)

    def action_view_chuyen_gc(self):
        action = self.env.ref('bsd_kinh_doanh.bsd_chuyen_gc_action').read()[0]

        chuyen_gc = self.env['bsd.chuyen_gc'].search([('bsd_giu_cho_id', '=', self.id)])
        if len(chuyen_gc) > 1:
            action['domain'] = [('id', 'in', chuyen_gc.ids)]
        elif chuyen_gc:
            form_view = [(self.env.ref('bsd_kinh_doanh.bsd_chuyen_gc_form').id, 'form')]
            if 'views' in action:
                action['views'] = form_view + [(state, view) for state, view in action['views'] if view != 'form']
            else:
                action['views'] = form_view
            action['res_id'] = chuyen_gc.id
        # Prepare the context.
        context = {
            'default_bsd_kh_ht_id': self.bsd_khach_hang_id.id,
            'default_bsd_giu_cho_id': self.id,
            'default_bsd_unit_id': self.bsd_unit_id.id,
            'default_bsd_du_an_id': self.bsd_du_an_id.id,
            'default_bsd_loai_gc': 'giu_cho'
        }
        action['context'] = context
        return action
