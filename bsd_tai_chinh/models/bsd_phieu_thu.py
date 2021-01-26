# -*- coding:utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError
import datetime
import logging
_logger = logging.getLogger(__name__)


class BsdPhieuThu(models.Model):
    _name = 'bsd.phieu_thu'
    _description = 'Phiếu thu'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _rec_name = 'bsd_so_pt'

    bsd_so_pt = fields.Char(string="Mã số", help="Số", required=True, readonly=True, copy=False,
                            default='/')
    _sql_constraints = [
        ('bsd_so_pt_unique', 'unique (bsd_so_pt)',
         'Số phiếu thu đã tồn tại !'),
    ]
    bsd_ngay_pt = fields.Datetime(string="Ngày thanh toán", help="Ngày thanh toán", required=True,
                                  readonly=True, default=lambda self: fields.Datetime.now(),
                                  states={'nhap': [('readonly', False)]})

    # @api.constrains('bsd_ngay_pt')
    # def _onchange_ngay_pt(self):
    #     today = datetime.date.today()
    #     if self.bsd_ngay_pt.date() > today:
    #         raise UserError(_("Ngày thanh toán không được lớn hơn ngày hiện tại."))

    def _get_pt(self):
        return self.env.ref('bsd_danh_muc.bsd_tien_mat').id

    bsd_loai_pt = fields.Selection([('tra_truoc', 'Trả trước'),
                                    ('gc_tc', 'Giữ chỗ thiện chí'),
                                    ('giu_cho', 'Giữ chỗ'),
                                    ('dat_coc', 'Đặt cọc'),
                                    ('hd', 'Hợp đồng')], default="tra_truoc", required=True, string="Loại",
                                   readonly=True,
                                   states={'nhap': [('readonly', False)]})
    bsd_khach_hang_id = fields.Many2one('res.partner', string="Khách hàng", help="Tên khách hàng", required=True,
                                        readonly=True,
                                        states={'nhap': [('readonly', False)]})
    bsd_pt_tt_id = fields.Many2one('bsd.pt_tt', string="Hình thức", help="Hình thức thanh toán",
                                   readonly=True, required=True, default=_get_pt,
                                   states={'nhap': [('readonly', False)]})
    bsd_so_nk = fields.Selection([('tien_mat', 'Tiền mặt'), ('ngan_hang', 'Ngân hàng')], string="Sổ nhật ký",
                                 required=True,
                                 readonly=True,
                                 states={'nhap': [('readonly', False)]}, default="tien_mat")
    bsd_tk_nh_id = fields.Many2one('res.partner.bank', string="Tài khoản ngân hàng",
                                   help="Số tài khoản ngân hàng của khách hàng",
                                   readonly=True,
                                   states={'nhap': [('readonly', False)]})
    bsd_ngan_hang_id = fields.Many2one('res.bank', string="Tên ngân hàng", help="Tên ngân hàng",
                                       readonly=True,
                                       states={'nhap': [('readonly', False)]})
    bsd_du_an_id = fields.Many2one('bsd.du_an', string="Dự án", help="Tên dự án", required=True,
                                   readonly=True,
                                   states={'nhap': [('readonly', False)]})
    bsd_unit_id = fields.Many2one('product.product', string="Sản phẩm",
                                  readonly=True,
                                  states={'nhap': [('readonly', False)]})
    bsd_gc_tc_id = fields.Many2one('bsd.gc_tc', string="Giữ chỗ thiện chí", help="Giữ chỗ thiện chí",
                                   readonly=True,
                                   states={'nhap': [('readonly', False)]})
    bsd_giu_cho_id = fields.Many2one('bsd.giu_cho', string="Giữ chỗ", help="Giữ chỗ",
                                     readonly=True,
                                     states={'nhap': [('readonly', False)]})
    bsd_dat_coc_id = fields.Many2one('bsd.dat_coc', string="Đặt cọc", help="Đặt cọc",
                                     readonly=True,
                                     states={'nhap': [('readonly', False)]})
    bsd_hd_ban_id = fields.Many2one('bsd.hd_ban', string="Hợp đồng", help="Hợp đồng",
                                    readonly=True,
                                    states={'nhap': [('readonly', False)]})
    bsd_tien_kh = fields.Monetary(string="Thanh toán", help="Số tiền thanh toán của khách hàng", required=True,
                                  readonly=True,
                                  states={'nhap': [('readonly', False)]})
    bsd_tien = fields.Monetary(string="Số tiền", help="Tiền thanh toán",
                               compute='_compute_tien_ct', store=True)
    bsd_tien_con_lai = fields.Monetary(string="Còn lại", help="Tiền còn lại",
                                       compute='_compute_tien_ct', store=True)
    bsd_ct_ids = fields.One2many('bsd.cong_no_ct', 'bsd_phieu_thu_id', string="Chi tiết TT", readonly=True,
                                 states={'nhap': [('readonly', False)]})
    bsd_dien_giai = fields.Char(string="Diễn giải", help="Diễn giải",
                                readonly=True,
                                states={'nhap': [('readonly', False)]})

    company_id = fields.Many2one('res.company', string='Công ty', default=lambda self: self.env.company)
    currency_id = fields.Many2one(related="company_id.currency_id", string="Tiền tệ", readonly=True)

    state = fields.Selection([('nhap', 'Nháp'),
                              ('da_gs', 'Xác nhận'),
                              ('huy', 'Hủy')], string="Trạng thái", help="Trạng thái",
                             required=True, readonly=True, default='nhap', tracking=1)
    bsd_tt_id = fields.Many2one('bsd.phieu_thu', string="TT trả trước",
                                help="Thanh toán trả trước khi thanh toán có dư", readonly=True)

    @api.onchange('bsd_du_an_id')
    def _onchange_du_an(self):
        self.bsd_gc_tc_id = False
        self.bsd_giu_cho_id = False
        self.bsd_dat_coc_id = False
        self.bsd_hd_ban_id = False
        self.bsd_unit_id = False

    @api.depends('bsd_ct_ids', 'bsd_ct_ids.state', 'bsd_tien')
    def _compute_tien_ct(self):
        for each in self:
            each.bsd_tien = sum(each.bsd_ct_ids.filtered(lambda x: x.state == 'hieu_luc').mapped('bsd_tien_pb'))
            each.bsd_tien_con_lai = each.bsd_tien_kh - each.bsd_tien

    # TC.01.01 Xác nhận phiếu thu
    def action_xac_nhan(self):
        # Kiểm tra nếu không có chi tiết không cho xác nhận với loại phiếu thu khác trả trước
        if self.bsd_loai_pt != 'tra_truoc':
            if not self.bsd_ct_ids:
                raise UserError(_("Không có chi tiết thanh toán. Vui lòng kiểm tra lại thông tin."))
        # Kiểm tra dự án
        if self.bsd_du_an_id.state != 'phat_hanh':
            raise UserError(_("Dự án đang ở giai đoạn chuẩn bị, không thể xác nhận giữ chỗ thiện chí."
                              "\nVui lòng kiểm tra lại thông tin."))
        # Kiểm tra hợp đồng đã bị thanh lý chưa
        if self.bsd_hd_ban_id.state == '12_thanh_ly':
            raise UserError(_('Hợp đồng đã bị thanh lý.\nVui lòng kiểm tra lại thông tin hợp đồng.'))
        # Kiểm tra nếu thu phí quản lý, phí bảo trì Sản phẩm phải có ngày cất nóc
        if self.bsd_loai_pt in ['pql', 'pbt']:
            if not self.bsd_unit_id.bsd_ngay_cn:
                raise UserError(_('Vui lòng kiểm tra thông tin sản phẩm trên hợp đồng.'))

        # Ghi nhận giờ ngày thanh toán
        now = datetime.datetime.now()
        get_time = self.bsd_ngay_pt.replace(hour=now.hour,
                                            minute=now.minute,
                                            second=now.second,
                                            microsecond=now.microsecond)
        # Ghi nhận công nợ cho thanh toán trả trước
        if self.bsd_loai_pt == 'tra_truoc':
            self._gs_pt_tra_truoc(time=get_time)
        # Ghi nhận công nợ cho các thanh toán khác
        elif self.bsd_loai_pt == 'hd':
            # Kiểm tra hợp đồng đã bị thanh lý chưa
            if self.bsd_hd_ban_id.state == '12_thanh_ly':
                raise UserError(_('Hợp đồng đã bị thanh lý.\nVui lòng kiểm tra lại thông tin hợp đồng.'))
            self.env['bsd.cong_no'].create({
                'bsd_chung_tu': self.bsd_so_pt,
                'bsd_ngay': get_time,
                'bsd_khach_hang_id': self.bsd_khach_hang_id.id,
                'bsd_du_an_id': self.bsd_du_an_id.id,
                'bsd_ps_giam': self.bsd_tien,
                'bsd_ps_tang': 0,
                'bsd_loai_ct': 'phieu_thu',
                'bsd_phat_sinh': 'giam',
                'bsd_phieu_thu_id': self.id,
                'state': 'da_gs',
            })
        else:
            self.env['bsd.cong_no'].create({
                'bsd_chung_tu': self.bsd_so_pt,
                'bsd_ngay': get_time,
                'bsd_khach_hang_id': self.bsd_khach_hang_id.id,
                'bsd_du_an_id': self.bsd_du_an_id.id,
                'bsd_ps_giam': self.bsd_tien,
                'bsd_ps_tang': 0,
                'bsd_loai_ct': 'phieu_thu',
                'bsd_phat_sinh': 'giam',
                'bsd_phieu_thu_id': self.id,
                'state': 'da_gs',
            })
        # Cập nhật trạng thái hiệu lực các chi tiết
        for ct in self.bsd_ct_ids:
            ct.write({
                'bsd_ngay_pb': get_time,
                'state': 'hieu_luc',
            })
            # Cập nhật trạng thái chứng từ gốc và số tiền thanh toán
            ct.kiem_tra_chung_tu()

        # Kiểm tra thanh toán dư để tạo thanh toán trả trước
        tien_du, tien_tt = self._kiem_tra_tt_du()
        if tien_du and self.bsd_loai_pt != 'tra_truoc':
            self.tao_tt_tra_truoc(tien_du=tien_du)
        self.write({
            'bsd_tien': tien_tt,
            'state': 'da_gs',
            'bsd_ngay_pt': get_time
        })

    # TC.01.02 Ghi sổ phiếu thu trả trước
    def _gs_pt_tra_truoc(self, time):
        self.env['bsd.cong_no'].create({
                'bsd_chung_tu': self.bsd_so_pt,
                'bsd_ngay': time,
                'bsd_khach_hang_id': self.bsd_khach_hang_id.id,
                'bsd_du_an_id': self.bsd_du_an_id.id,
                'bsd_ps_giam': self.bsd_tien_kh,
                'bsd_ps_tang': 0,
                'bsd_loai_ct': 'phieu_thu',
                'bsd_phat_sinh': 'giam',
                'bsd_phieu_thu_id': self.id,
                'state': 'da_gs',
            })

    # TC.01.08 - Kiểm tra thanh toán dư
    def _kiem_tra_tt_du(self):
        bsd_tien_kh = self.bsd_tien_kh
        bsd_tien_tt = sum(self.bsd_ct_ids.filtered(lambda x: x.state == 'hieu_luc').mapped('bsd_tien_pb'))
        bsd_tien_du = bsd_tien_kh - bsd_tien_tt
        return bsd_tien_du, bsd_tien_tt

    # TC.01.12 Cấn trừ công nợ phiếu thu
    def action_can_tru(self):    
        if self.bsd_hd_ban_id.state == '12_thanh_ly':
            raise UserError(_('Hợp đồng đã bị thanh lý.\nVui lòng kiểm tra lại thông tin!'))
        return {
            'type': 'ir.actions.act_window',
            'name': 'Cấn trừ công nợ',
            'res_model': 'bsd.can_tru',
            'view_mode': 'form',
            'target': 'current',
            'context': {'default_bsd_khach_hang_id': self.bsd_khach_hang_id.id,
                        'default_bsd_hd_ban_id': self.bsd_hd_ban_id.id,
                        'default_bsd_phieu_thu_id': self.id,
                        }
        }

    # Action in phiếu thu
    def action_in(self):
        return self.env.ref('bsd_tai_chinh.bsd_phieu_thu_report_action').read()[0]

    # Action hủy
    def action_huy(self):
        if self.state == 'nhap':
            self.write({'state': 'huy'})
            self.bsd_ct_ids.write({
                'state': 'vo_hieu_luc'
            })

    @api.model
    def create(self, vals):
        if 'bsd_du_an_id' in vals:
            du_an = self.env['bsd.du_an'].browse(vals['bsd_du_an_id'])
            sequence = du_an.get_ma_bo_cn(loai_cn=self._name)
        # Tạo dữ liệu khách hàng khi import giữ chỗ thiện chí
        if 'bsd_gc_tc_id' in vals:
            gc_tc = self.env['bsd.gc_tc'].browse(vals['bsd_gc_tc_id'])
            vals['bsd_khach_hang_id'] = gc_tc.bsd_khach_hang_id.id
        if 'bsd_giu_cho_id' in vals:
            giu_cho = self.env['bsd.giu_cho'].browse(vals['bsd_giu_cho_id'])
            vals['bsd_khach_hang_id'] = giu_cho.bsd_khach_hang_id.id
        if 'bsd_dat_coc_id' in vals:
            dat_coc = self.env['bsd.dat_coc'].browse(vals['bsd_dat_coc_id'])
            vals['bsd_khach_hang_id'] = dat_coc.bsd_khach_hang_id.id
        # nhớ xóa sau khi import
        if not sequence:
            raise UserError(_('Dự án chưa có mã phiếu thu.'))
        vals['bsd_so_pt'] = sequence.next_by_id()
        res = super(BsdPhieuThu, self).create(vals)
        # Tự động xác nhận giữ chỗ thiện chí
        # res.action_xac_nhan()
        # nhớ xóa sau khi import
        return res

    def _get_name(self):
        pt = self
        name = pt.bsd_so_pt or ''
        if self._context.get('show_info'):
            name = "%s - %s" % (pt.bsd_so_pt, '{:,.0f} đ'.format(pt.bsd_tien_con_lai).replace(',', '.'))
        return name

    def name_get(self):
        res = []
        for pt in self:
            name = pt._get_name()
            res.append((pt.id, name))
        return res

    # Tạo ra thanh toán trả trước khi thanh toán dư
    def tao_tt_tra_truoc(self, tien_du=0):
        tra_truoc = self.env['bsd.phieu_thu'].create({
                        'bsd_loai_pt': 'tra_truoc',
                        'bsd_khach_hang_id': self.bsd_khach_hang_id.id,
                        'bsd_du_an_id': self.bsd_du_an_id.id,
                        'bsd_pt_tt_id': self.bsd_pt_tt_id.id,
                        'bsd_tien_kh': tien_du,
                    })
        tra_truoc.action_xac_nhan()
        self.write({'bsd_tt_id': tra_truoc.id})
