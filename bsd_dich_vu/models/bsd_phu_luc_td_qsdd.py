# -*- coding:utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError
from odoo.tools.float_utils import float_round
import logging
_logger = logging.getLogger(__name__)


class BsdPLQSDD(models.Model):
    _name = 'bsd.pl_qsdd'
    _description = "Phụ lục thay đổi giá trị quyền sử dụng đất"
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _rec_name = 'bsd_ma'

    bsd_ma = fields.Char(string="Mã", help="Mã phụ lục hợp đồng thay đổi giá trị quyền sử dụng đất",
                         required=True, readonly=True,
                         copy=False, default='/')
    _sql_constraints = [
        ('bsd_ma_unique', 'unique (bsd_ma)',
         'Mã phụ lục hợp đồng đã tồn tại !'),
    ]
    bsd_ngay = fields.Datetime(string="Ngày", help="Ngày tạo phụ lục hợp đồng thay đổi giá trị quyền sử dụng đất",
                               required=True,
                               default=lambda self: fields.Datetime.now(),
                               readonly=True,
                               states={'nhap': [('readonly', False)]})
    bsd_khach_hang_id = fields.Many2one('res.partner', string="Khách hàng", help="Tên khách hàng", required=True,
                                        readonly=True,
                                        states={'nhap': [('readonly', False)]})
    bsd_hd_ban_id = fields.Many2one('bsd.hd_ban', string="Hợp đồng", help="Hợp đồng mua bán", required=True,
                                    readonly=True,
                                    states={'nhap': [('readonly', False)]})
    bsd_cs_tt_ht_id = fields.Many2one('bsd.cs_tt', string="PTTT hiện tại", readonly=True, required=True)
    bsd_ltt_ht_ids = fields.Many2many('bsd.lich_thanh_toan', relation='bsd_lich_ht_qsdd_rel',
                                      string="Lịch thanh toán ht", readonly=True)

    @api.onchange('bsd_hd_ban_id')
    def _onchange_hd(self):
        self.bsd_du_an_id = self.bsd_hd_ban_id.bsd_du_an_id
        self.bsd_unit_id = self.bsd_hd_ban_id.bsd_unit_id
        self.bsd_cs_tt_ht_id = self.bsd_hd_ban_id.bsd_cs_tt_id
        self.update({
            'bsd_ltt_ht_ids': [(5,), (6, 0, self.bsd_hd_ban_id.bsd_ltt_ids.ids)],
        })
        self.bsd_gia_ban_ht = self.bsd_hd_ban_id.bsd_gia_ban
        self.bsd_tien_ck_ht = self.bsd_hd_ban_id.bsd_tien_ck
        self.bsd_tien_bg_ht = self.bsd_hd_ban_id.bsd_tien_bg
        self.bsd_gia_truoc_thue_ht = self.bsd_hd_ban_id.bsd_gia_truoc_thue
        self.bsd_tien_qsdd_ht = self.bsd_hd_ban_id.bsd_tien_qsdd
        self.bsd_tien_thue_ht = self.bsd_hd_ban_id.bsd_tien_thue
        self.bsd_tien_pbt_ht = self.bsd_hd_ban_id.bsd_tien_pbt
        self.bsd_tong_gia_ht = self.bsd_hd_ban_id.bsd_tong_gia
        self.bsd_tien_da_tt = sum(self.bsd_hd_ban_id.bsd_ltt_ids
                                  .filtered(lambda l: l.bsd_thanh_toan != 'chua_tt').mapped('bsd_tien_dot_tt'))
        self.bsd_thue_suat = self.bsd_hd_ban_id.bsd_thue_suat
        self.bsd_qsdd_m2_ht = self.bsd_hd_ban_id.bsd_qsdd_m2
        # tự động load đợt cấn trừ , mặc định đợt cuối
        self.bsd_dot_ct_id = self.bsd_hd_ban_id.bsd_ltt_ids.filtered(lambda d: d.bsd_ma_dtt == 'DBGC')

    bsd_du_an_id = fields.Many2one('bsd.du_an', string="Dự án",
                                   help="Tên dự án", required=True, readonly=True)
    bsd_unit_id = fields.Many2one('product.product',
                                  string="Sản phẩm", help="Tên Sản phẩm",
                                  required=True, readonly=True)

    @api.onchange('bsd_unit_id')
    def _onchange_unit(self):
        self.bsd_dt_sd = self.bsd_hd_ban_id.bsd_dt_sd

    bsd_dt_sd = fields.Float(string="Diện tích sử dụng", help="Diện tích sử dụng", readonly=True)
    bsd_cl_thue = fields.Monetary(string="chênh lệch thuế", help="Chênh lệch tiền thuế khi thay đổi giá trị QSDĐ",
                                  compute='_compute_cl_thue', store=True)

    @api.depends('bsd_tien_qsdd_moi')
    def _compute_cl_thue(self):
        for each in self:
            each.bsd_cl_thue = each.bsd_tien_thue_moi - each.bsd_tien_thue_ht

    bsd_dien_giai = fields.Char(string="Diễn giải", help="Diễn giải",
                                readonly=True,
                                states={'nhap': [('readonly', False)]})
    bsd_tien_da_tt = fields.Monetary(string="Tiền đã TT", help="Tổng tiền đợt đã và đang thanh toán 1 phần của hợp đồng",
                                     readonly=True)

    # field giá hiện tại
    bsd_tien_ck_ht = fields.Monetary(string="Tiền chiết khấu", help="Tiền chiết khấu hiện tại", readonly=True)
    bsd_qsdd_m2_ht = fields.Monetary(string="QSDĐ/ m2 hiện tại", help="Giá trị quyền sử dụng đất trên m2", readonly=True)
    bsd_gia_ban_ht = fields.Monetary(string="Giá bán", help="Giá bán", readonly=True)
    bsd_tien_bg_ht = fields.Monetary(string="Giá trị ĐKBG", help="Tổng tiền bàn giao", readonly=True)
    bsd_gia_truoc_thue_ht = fields.Monetary(string="Giá bán trước thuế",
                                            help="""Giá bán trước thuế: bằng giá bán cộng tiền bàn giao trừ 
                                            chiết khấu""",
                                            readonly=True)
    bsd_tien_qsdd_ht = fields.Monetary(string="Giá trị QSDĐ",
                                       help="""Giá trị sử dụng đất: bằng QSDĐ/m2 nhân với diện tích sử dung""",
                                       readonly=True)
    bsd_tien_thue_ht = fields.Monetary(string="Tiền thuế hiện tại",
                                       help="""Tiền thuế: Giá bán trước thuế trừ giá trị QSDĐ, nhân với thuế suất""",
                                       readonly=True)
    bsd_tien_pbt_ht = fields.Monetary(string="Phí bảo trì", help="Phí bảo trì: bằng % phí bảo trì nhân với giá bán",
                                      readonly=True)
    bsd_tong_gia_ht = fields.Monetary(string="Tổng giá bán",
                                      help="""Tổng giá bán: bằng Giá bán trước thuế cộng Tiền thuế cộng phí bảo trì""",
                                      readonly=True)
    # field giá bán mới
    bsd_qsdd_m2_moi = fields.Monetary(string="QSDĐ/ m2 mới", help="Giá trị quyền sử dụng đất trên m2 mới",
                                      readonly=True, states={'nhap': [('readonly', False)]})
    bsd_gia_ban_moi = fields.Monetary(string="Giá bán", help="Giá bán", readonly=True)
    bsd_tien_ck_moi = fields.Monetary(string="Tiền chiết khấu", help="Tiền chiết khấu", readonly=True)
    bsd_tien_bg_moi = fields.Monetary(string="Giá trị ĐKBG", help="Tổng tiền bàn giao", readonly=True)
    bsd_gia_truoc_thue_moi = fields.Monetary(string="Giá bán trước thuế",
                                             help="""Giá bán trước thuế: bằng giá bán cộng tiền bàn giao trừ 
                                             chiết khấu""", compute='_compute_gia_truoc_thue', store=True,
                                             readonly=True)
    bsd_tien_qsdd_moi = fields.Monetary(string="Giá trị QSDĐ",
                                        help="""Giá trị sử dụng đất: bằng QSDĐ/m2 nhân với diện tích sử dung""",
                                        readonly=True, compute='_compute_qsdd', store=True)
    bsd_tien_thue_moi = fields.Monetary(string="Tiền thuế mới",
                                        help="""Tiền thuế: Giá bán trước thuế trừ giá trị QSDĐ, nhân với thuế suất""",
                                        readonly=True, compute='_compute_tien_thue', store=True)
    bsd_tien_pbt_moi = fields.Monetary(string="Phí bảo trì", help="Phí bảo trì: bằng % phí bảo trì nhân với giá bán",
                                       readonly=True)
    bsd_tong_gia_moi = fields.Monetary(string="Tổng giá bán",
                                       help="""Tổng giá bán: bằng Giá bán trước thuế cộng Tiền thuế cộng phí bảo trì""",
                                       readonly=True, compute='_compute_tong_gia', store=True)

    bsd_ngay_ky_pl = fields.Date(string="Ngày ký PL", help="Ngày ký phụ lục hợp đồng", readonly=True)
    bsd_nguoi_xn_ky_id = fields.Many2one('res.users', string="Người xác nhận ký",
                                         help="Người xác nhận ký phụ lục hợp đồng", readonly=True)
    bsd_ngay_duyet = fields.Date(string="Ngày duyệt", help="Ngày duyệt phụ lục hợp đồng", readonly=True)
    bsd_nguoi_duyet_id = fields.Many2one('res.users', string="Người duyệt", readonly=True)
    bsd_nguoi_xn_id = fields.Many2one('res.users', string="Người xác nhận", readonly=True)
    bsd_ngay_xn = fields.Date(string="Ngày xác nhận", help="Ngày xác nhận phụ lục hợp đồng", readonly=True)
    bsd_nguoi_huy_id = fields.Many2one('res.users', string="Người hủy", readonly=True)
    bsd_ngay_huy = fields.Date(string="Ngày hủy", help="Ngày hủy phụ lục hợp đồng", readonly=True)
    bsd_ly_do_huy = fields.Char(string="Lý do hủy", help="Lý do hủy phụ lục", readonly=True)
    state = fields.Selection([('nhap', 'Nháp'), ('xac_nhan', 'Xác nhận'), ('duyet', 'Duyệt'),
                              ('dk_pl', 'Đã ký phụ lục'), ('huy', 'Hủy')],
                             string="Trạng thái", help="Trạng thái", required=True, default="nhap", tracking=1)
    bsd_ly_do = fields.Char(string="Lý do không duyệt", readonly=True, tracking=2)
    company_id = fields.Many2one('res.company', string='Công ty', default=lambda self: self.env.company)
    currency_id = fields.Many2one(related="company_id.currency_id", string="Tiền tệ", readonly=True)
    bsd_thue_suat = fields.Float(string="Thuế suất", help="Thuế suất", readonly=True)

    bsd_dot_ct_id = fields.Many2one('bsd.lich_thanh_toan', string="Đợt cấn trừ", readonly=True,
                                         states={'nhap': [('readonly', False)]})

    @api.depends('bsd_qsdd_m2_moi')
    def _compute_qsdd(self):
        for each in self:
            each.bsd_tien_qsdd_moi = each.bsd_dt_sd * each.bsd_qsdd_m2_moi

    @api.depends('bsd_thue_suat', 'bsd_gia_truoc_thue_moi', 'bsd_tien_qsdd_moi')
    def _compute_tien_thue(self):
        for each in self:
            each.bsd_tien_thue_moi = (each.bsd_gia_truoc_thue_moi - each.bsd_tien_qsdd_moi) * each.bsd_thue_suat / 100

    @api.depends('bsd_gia_ban_moi', 'bsd_tien_ck_moi', 'bsd_tien_bg_moi')
    def _compute_gia_truoc_thue(self):
        for each in self:
            each.bsd_gia_truoc_thue_moi = each.bsd_gia_ban_moi - each.bsd_tien_ck_moi + each.bsd_tien_bg_moi

    @api.depends('bsd_gia_truoc_thue_moi', 'bsd_tien_thue_moi', 'bsd_tien_pbt_moi')
    def _compute_tong_gia(self):
        for each in self:
            each.bsd_tong_gia_moi = each.bsd_gia_truoc_thue_moi + each.bsd_tien_thue_moi + each.bsd_tien_pbt_moi

    def action_tao_pl(self):
        return {
            'type': 'ir.actions.act_window',
            'name': 'Phụ lục thay đổi giá trị QSDĐ',
            'res_model': 'bsd.pl_qsdd',
            'res_id': self.id,
            'target': 'current',
            'view_mode': 'form'
        }

    # Xác nhận phụ lục hợp đồng
    def action_xac_nhan(self):
        if not self.bsd_ltt_ids:
            raise UserError(_("Chưa tạo lịch thanh toán mới.\nVui lòng kiểm tra lại thông tin."))
        self.write({
            'state': 'xac_nhan',
            'bsd_nguoi_xn_id': self.env.uid,
            'bsd_ngay_xn': fields.Date.today(),
        })

    def action_duyet(self):
        if self.state == 'xac_nhan':
            self.write({
                'bsd_nguoi_duyet_id': self.env.uid,
                'bsd_ngay_duyet': fields.Date.today(),
                'state': 'duyet',
            })

    # Ký phụ lục hợp đồng
    def action_ky_pl(self):
        if self.state == 'duyet':
            action = self.env.ref('bsd_dich_vu.bsd_wizard_ky_pl_action').read()[0]
            return action

    # Hủy phụ lục hợp đồng
    def action_huy(self):
        if self.state in ['nhap', 'xac_nhan']:
            return self.env.ref('bsd_dich_vu.bsd_wizard_huy_pl_action').read()[0]

    # Không duyệt phụ lục hợp đồng
    def action_khong_duyet(self):
        if self.state == 'xac_nhan':
            action = self.env.ref('bsd_dich_vu.bsd_wizard_khong_duyet_pl_action').read()[0]
            return action

    @api.model
    def create(self, vals):
        sequence = self.env['ir.sequence']
        if 'bsd_du_an_id' in vals:
            du_an = self.env['bsd.du_an'].browse(vals['bsd_du_an_id'])
            sequence = du_an.get_ma_bo_cn(loai_cn=self._name)
        if not sequence:
            raise UserError(_('Dự án chưa có quy định mã phụ lục thay đổi giá trị QSDĐ.\n'
                              'Vui lòng kiểm tra lại thông tin.'))
        vals['bsd_ma'] = sequence.next_by_id()
        res = super(BsdPLQSDD, self).create(vals)
        res.write({
            'bsd_gia_ban_moi': res.bsd_gia_ban_ht,
            'bsd_tien_ck_moi': res.bsd_tien_ck_ht,
            'bsd_tien_bg_moi': res.bsd_tien_bg_ht,
            'bsd_tien_pbt_moi': res.bsd_tien_pbt_ht,
        })
        return res

