# -*- coding:utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError
from odoo.tools.float_utils import float_round
import logging
_logger = logging.getLogger(__name__)


class BsdPLCLDT(models.Model):
    _name = 'bsd.pl_cldt'
    _description = "Phụ lục điều chỉnh chênh lệch diện tích"
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _rec_name = 'bsd_ma'

    bsd_ma = fields.Char(string="Mã", help="Mã phụ lục điều chỉnh chênh lệch diện tích",
                         required=True, readonly=True,
                         copy=False, default='/')
    _sql_constraints = [
        ('bsd_ma_unique', 'unique (bsd_ma)',
         'Mã phụ lục hợp đồng đã tồn tại !'),
    ]
    bsd_ngay = fields.Datetime(string="Ngày", help="Ngày phụ lục điều chỉnh chênh lệch diện tích",
                               required=True,
                               default=lambda self: fields.Datetime.now(),
                               readonly=True,
                               states={'nhap': [('readonly', False)]})
    bsd_khach_hang_id = fields.Many2one('res.partner', string="Khách hàng", help="Tên khách hàng", required=True,
                                        readonly=True)
    bsd_hd_ban_id = fields.Many2one('bsd.hd_ban', string="Hợp đồng", help="Hợp đồng mua bán", required=True,
                                    readonly=True)
    bsd_du_an_id = fields.Many2one('bsd.du_an', string="Dự án",
                                   help="Tên dự án", required=True, readonly=True)
    bsd_unit_id = fields.Many2one('product.product',
                                  string="Sản phẩm", help="Tên Sản phẩm",
                                  required=True, readonly=True)
    bsd_dot_tt_id = fields.Many2one('bsd.lich_thanh_toan', string="Đợt TT", required=True,
                                    readonly=True, help="Đợt thanh toán gắn phí phát sinh",
                                    states={'nhap': [('readonly', False)]})
    bsd_cn_dttt_unit_id = fields.Many2one('bsd.cn_dttt_unit', string="CN.DTTT chi tiết",
                                          help="Chi tiết cập nhật diện tích thông thủy thực tế của sản phẩm",
                                          readonly=True)
    bsd_cl_tt = fields.Float(string="CL thực tế", help="Phầm trăm chênh lệch thực tế sau khi đo đạt",
                             readonly=True, digits=(2, 2))
    bsd_cl_cp = fields.Float(string="CL cho phép", help="Phần trăm chênh lệch cho phép của sản phẩm",
                             readonly=True)

    @api.onchange('bsd_unit_id')
    def _onchange_unit(self):
        self.bsd_dt_sd = self.bsd_unit_id.bsd_dt_sd
        self.bsd_dt_tt = self.bsd_unit_id.bsd_dt_tt

    bsd_dt_tt_tk = fields.Float(string="Diện tích sử dụng", help="Diện tích sử dụng", readonly=True)
    bsd_dt_tt_tt = fields.Float(string="Diện tích thực tế", help="Diện tích thực tế", readonly=True)

    bsd_dien_giai = fields.Char(string="Diễn giải", help="Diễn giải",
                                readonly=True,
                                states={'nhap': [('readonly', False)]})
    bsd_tien_da_tt = fields.Monetary(string="Tiền đã TT", help="Tổng tiền đợt đã và đang thanh toán 1 phần của hợp đồng",
                                     readonly=True)

    # field giá hiện tại
    bsd_thue_suat = fields.Float(string="Thuế suất", help="Thuế suất", readonly=True)
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
    bsd_tong_gia_ko_pbt_ht = fields.Monetary(string="Tổng giá bán (không bao gồm PBT)",
                                             help="Công thức: bằng giá bán trước thuế cộng tiền thuế", readonly=True)
    bsd_tong_gia_ht = fields.Monetary(string="Tổng giá bán",
                                      help="""Tổng giá bán: bằng Giá bán trước thuế cộng Tiền thuế cộng phí bảo trì""",
                                      readonly=True)
    bsd_tien_pql_ht = fields.Monetary(string="Phí quản lý", help="Số tiền phí quản lý hiện tại", readonly=True)

    # field giá bán mới
    bsd_dg_tt = fields.Monetary(string="Đơn giá tt (thiết kế)", help="Đơn giá thông thủy", readonly=True)
    bsd_cl_dt = fields.Float(string="Chênh lệch diện tích", help="Chênh lệch diện tích", readonly=True)
    bsd_gia_truoc_thue_moi = fields.Monetary(string="Giá bán trước thuế",
                                             help="""Giá bán trước thuế: bằng giá bán cộng tiền bàn giao trừ 
                                             chiết khấu""",
                                             readonly=True)
    bsd_tien_thue_moi = fields.Monetary(string="Tiền thuế mới",
                                        help="""Tiền thuế: Giá bán trước thuế trừ giá trị QSDĐ, nhân với thuế suất""",
                                        readonly=True)
    bsd_tong_gia_ko_pbt_moi = fields.Monetary(string="Tổng giá bán mới (không bao gồm PBT)",
                                              compute='_compute_gia_ko_pbt', store=True,
                                              help="Công thức: bằng giá bán trước thuế cộng tiền thuế", readonly=True)

    @api.depends('bsd_tien_thue_moi', 'bsd_gia_truoc_thue_moi')
    def _compute_gia_ko_pbt(self):
        for each in self:
            each.bsd_tong_gia_ko_pbt_moi = each.bsd_tien_thue_moi + each.bsd_gia_truoc_thue_moi
    bsd_tien_pbt_moi = fields.Monetary(string="Phí bảo trì mới",
                                       help="Phí bảo trì: bằng % phí bảo trì nhân với giá bán",
                                       readonly=True)
    bsd_tien_pql_moi = fields.Monetary(string="Phí quản lý mới", help="Số tiền phí quản lý mới", readonly=True)
    bsd_cl_pbt = fields.Monetary(string="Chênh lệch PBT", help="Chênh lệch phí bảo trì", readonly=True)
    bsd_cl_hd = fields.Monetary(string="Chênh lệch HĐ", help="Chênh lệch hợp đồng", readonly=True)
    bsd_cl_pql = fields.Monetary(string="Chênh lệch PQL", help="Chênh lệch phí quản lý", readonly=True)
    bsd_tong_cl = fields.Monetary(string="Tổng chênh lệch", help="Tổng giá trị chênh lệch", compute='_compute_tong_cl',
                                  store=True,
                                  readonly=True)

    @api.depends('bsd_cl_pbt', 'bsd_cl_hd', 'bsd_cl_pql')
    def _compute_tong_cl(self):
        for each in self:
            each.bsd_tong_cl = each.bsd_cl_pbt + each.bsd_cl_pql + each.bsd_cl_hd
    # field xác nhận
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

    # Xác nhận phụ lục hợp đồng
    def action_xac_nhan(self):
        # Kiểm tra hợp đồng đã bị thanh lý chưa
        if self.bsd_hd_ban_id.state == 'thanh_ly':
            raise UserError(_("Hợp đồng đã bị thanh lý.\nVui lòng kiểm tra lại thông tin."))
        # Kiểm tra đợt thanh toán chưa thanh toán hoàn tất
        if self.bsd_dot_tt_id.bsd_thanh_toan == 'da_tt':
            raise UserError(_("Đợt thanh toán đã thanh toán hoàn tất.\nVui lòng kiểm tra lại thông tin."))
        if self.bsd_dot_tt_id.bsd_hd_ban_id.id != self.bsd_hd_ban_id.id:
            raise UserError(_("Đợt thanh toán đã hết hiệu lực.\nVui lòng kiểm tra lại thông tin."))

        self.write({
            'state': 'xac_nhan',
            'bsd_nguoi_xn_id': self.env.uid,
            'bsd_ngay_xn': fields.Date.today(),
        })

    def action_duyet(self):
        # Kiểm tra hợp đồng đã bị thanh lý chưa
        if self.bsd_hd_ban_id.state == 'thanh_ly':
            raise UserError(_("Hợp đồng đã bị thanh lý.\nVui lòng kiểm tra lại thông tin."))
        if self.state == 'xac_nhan':
            self.write({
                'bsd_nguoi_duyet_id': self.env.uid,
                'bsd_ngay_duyet': fields.Date.today(),
                'state': 'duyet',
            })

    # Ký phụ lục hợp đồng
    def action_ky_pl(self):
        # Kiểm tra hợp đồng đã bị thanh lý chưa
        if self.bsd_hd_ban_id.state == 'thanh_ly':
            raise UserError(_("Hợp đồng đã bị thanh lý.\nVui lòng kiểm tra lại thông tin."))
        if self.state == 'duyet':
            action = self.env.ref('bsd_dich_vu.bsd_wizard_ky_pl_action').read()[0]
            return action

    # Cập nhật thông tin sau khi xác nhận ký hợp đồng
    def thay_doi_cldt(self):
        # Kiểm tra tổng tiền chênh lệch âm tạo thanh toán trả trước cho khách hàng
        if self.bsd_tong_cl < 0:
            phieu_thu = self.env['bsd.phieu_thu'].create({
                            'bsd_du_an_id': self.bsd_du_an_id.id,
                            'bsd_khach_hang_id': self.bsd_khach_hang_id.id,
                            'bsd_tien_kh': abs(self.bsd_tong_cl),
                            'bsd_loai_pt': 'tra_truoc',
                            'bsd_dien_giai': "Phát sinh từ phụ lục điều chỉnh chênh lệch diện tích"
                        })
            phieu_thu.action_xac_nhan()
            self.write({
                'bsd_phieu_thu_id': phieu_thu.id,
            })
        else:
            phi_ps = self.env['bsd.phi_ps'].create({
                'bsd_ten_ps': "Phí phát sinh khi cập nhật diện tích sản phẩm " + self.bsd_unit_id.bsd_ma_unit,
                'bsd_du_an_id': self.bsd_du_an_id.id,
                'bsd_hd_ban_id': self.bsd_hd_ban_id.id,
                'bsd_unit_id': self.bsd_unit_id.id,
                'bsd_khach_hang_id': self.bsd_khach_hang_id.id,
                'bsd_dot_tt_id': self.bsd_dot_tt_id.id,
                'bsd_loai': 'pl_hd',
                'bsd_tien_ps': self.bsd_tong_cl,
            })
            phi_ps.action_xac_nhan()
            self.write({
                'bsd_phi_ps_id': phi_ps.id
            })

    # Hủy phụ lục hợp đồng
    def action_huy(self):
        if self.state in ['nhap', 'xac_nhan']:
            return self.env.ref('bsd_dich_vu.bsd_wizard_huy_pl_action').read()[0]

    # Không duyệt phụ lục hợp đồng
    def action_khong_duyet(self):
        if self.state == 'xac_nhan':
            action = self.env.ref('bsd_dich_vu.bsd_wizard_khong_duyet_pl_action').read()[0]
            return action

    def action_view_thanh_toan(self):
        action = self.env.ref('bsd_tai_chinh.bsd_phieu_thu_action').read()[0]

        form_view = [(self.env.ref('bsd_tai_chinh.bsd_phieu_thu_form').id, 'form')]
        if 'views' in action:
            action['views'] = form_view + [(state, view) for state, view in action['views'] if view != 'form']
        else:
            action['views'] = form_view
        action['res_id'] = self.bsd_phieu_thu_id.id
        return action

    @api.model
    def create(self, vals):
        sequence = self.env['ir.sequence']
        if 'bsd_du_an_id' in vals:
            du_an = self.env['bsd.du_an'].browse(vals['bsd_du_an_id'])
            sequence = du_an.get_ma_bo_cn(loai_cn=self._name)
        if not sequence:
            raise UserError(_('Dự án chưa có quy định mã phụ lục điều chỉnh chênh lệch diện tích.\n'
                              'Vui lòng kiểm tra lại thông tin.'))
        vals['bsd_ma'] = sequence.next_by_id()
        hd = self.env['bsd.hd_ban'].browse(vals['bsd_hd_ban_id'])
        vals['bsd_khach_hang_id'] = hd.bsd_khach_hang_id.id
        return super(BsdPLCLDT, self).create(vals)

