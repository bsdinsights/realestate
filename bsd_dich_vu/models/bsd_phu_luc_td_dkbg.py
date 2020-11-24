# -*- coding:utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError
from odoo.tools.float_utils import float_round
import logging
_logger = logging.getLogger(__name__)


class BsdPLDKBG(models.Model):
    _name = 'bsd.pl_dkbg'
    _description = "Phụ lục thay đổi điều kiện bàn giao"
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _rec_name = 'bsd_ma'

    bsd_ma = fields.Char(string="Mã", help="Mã phụ lục hợp đồng thay đổi điều kiện bàn giao",
                         required=True, readonly=True,
                         copy=False, default='/')
    _sql_constraints = [
        ('bsd_ma_unique', 'unique (bsd_ma)',
         'Mã phụ lục hợp đồng đã tồn tại !'),
    ]
    bsd_ngay = fields.Datetime(string="Ngày", help="Ngày tạo phụ lục hợp đồng thay đổi điều kiện bàn giao",
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
    bsd_ltt_ht_ids = fields.Many2many('bsd.lich_thanh_toan', relation='lich_ht_dkbg_rel', string="Lịch thanh toán ht", readonly=True)
    bsd_bg_ht_ids = fields.Many2many('bsd.ban_giao', relation='dkbg_pl_ht_rel',
                                     readonly=True, string="ĐKBG hiện tại")

    @api.onchange('bsd_hd_ban_id')
    def _onchange_hd(self):
        self.bsd_du_an_id = self.bsd_hd_ban_id.bsd_du_an_id
        self.bsd_unit_id = self.bsd_hd_ban_id.bsd_unit_id
        self.bsd_cs_tt_ht_id = self.bsd_hd_ban_id.bsd_cs_tt_id
        self.update({
            'bsd_ltt_ht_ids': [(5,), (6, 0, self.bsd_hd_ban_id.bsd_ltt_ids.ids)],
            'bsd_bg_ht_ids': [(5,), (6, 0, self.bsd_hd_ban_id.bsd_bg_ids.ids)],
        })
        self.bsd_gia_ban_ht = self.bsd_hd_ban_id.bsd_gia_ban
        self.bsd_tien_ck_ht = self.bsd_hd_ban_id.bsd_tien_ck
        self.bsd_tien_bg_ht = self.bsd_hd_ban_id.bsd_tien_bg
        self.bsd_gia_truoc_thue_ht = self.bsd_hd_ban_id.bsd_gia_truoc_thue
        self.bsd_tien_qsdd_ht = self.bsd_hd_ban_id.bsd_tien_qsdd
        self.bsd_tien_thue_ht = self.bsd_hd_ban_id.bsd_tien_thue
        self.bsd_tien_pbt_ht = self.bsd_hd_ban_id.bsd_tien_pbt
        self.bsd_tong_gia_ht = self.bsd_hd_ban_id.bsd_tong_gia
        self.bsd_tien_da_tt = self.bsd_hd_ban_id.bsd_tien_tt_hd
        self.bsd_thue_suat = self.bsd_hd_ban_id.bsd_thue_suat

    bsd_du_an_id = fields.Many2one('bsd.du_an', string="Dự án",
                                   help="Tên dự án", required=True, readonly=True)
    bsd_unit_id = fields.Many2one('product.product',
                                  string="Sản phẩm", help="Tên Sản phẩm",
                                  required=True, readonly=True)
    bsd_dien_giai = fields.Char(string="Diễn giải", help="Diễn giải",
                                readonly=True,
                                states={'nhap': [('readonly', False)]})
    bsd_tien_da_tt = fields.Monetary(string="Tiền đã TT", help="Tổng tiền đợt đã và đang thanh toán 1 phần của hợp đồng",
                                     readonly=True)
    bsd_tien_ck_ht = fields.Monetary(string="Tiền CK hiện tại", help="Tiền chiết khấu hiện tại", readonly=True)
    bsd_dkbg_moi_ids = fields.Many2many('bsd.dk_bg', relation='bsd_dkbg_pl_moi_rel',
                                        readonly=True, string="ĐKBG mới")

    # field giá hiện tại
    bsd_gia_ban_ht = fields.Monetary(string="Giá bán", help="Giá bán", readonly=True)
    bsd_tien_bg_ht = fields.Monetary(string="Giá trị ĐKBG", help="Tổng tiền bàn giao", readonly=True)
    bsd_gia_truoc_thue_ht = fields.Monetary(string="Giá bán trước thuế",
                                            help="""Giá bán trước thuế: bằng giá bán cộng tiền bàn giao trừ 
                                            chiết khấu""",
                                            readonly=True)
    bsd_tien_qsdd_ht = fields.Monetary(string="Giá trị QSDĐ",
                                       help="""Giá trị sử dụng đất: bằng QSDĐ/m2 nhân với diện tích sử dung""",
                                       readonly=True)
    bsd_tien_thue_ht = fields.Monetary(string="Tiền thuế",
                                       help="""Tiền thuế: Giá bán trước thuế trừ giá trị QSDĐ, nhân với thuế suất""",
                                       readonly=True)
    bsd_tien_pbt_ht = fields.Monetary(string="Phí bảo trì", help="Phí bảo trì: bằng % phí bảo trì nhân với giá bán",
                                      readonly=True)
    bsd_tong_gia_ht = fields.Monetary(string="Tổng giá bán",
                                      help="""Tổng giá bán: bằng Giá bán trước thuế cộng Tiền thuế cộng phí bảo trì""",
                                      readonly=True)
    # field giá bán mới
    bsd_gia_ban_moi = fields.Monetary(string="Giá bán", help="Giá bán", readonly=True)
    bsd_tien_ck_moi = fields.Monetary(string="Tiền CK mới", help="Tiền chiết khấu", readonly=True)
    bsd_tien_bg_moi = fields.Monetary(string="Giá trị ĐKBG", help="Tổng tiền bàn giao", readonly=True)
    bsd_gia_truoc_thue_moi = fields.Monetary(string="Giá bán trước thuế",
                                             help="""Giá bán trước thuế: bằng giá bán cộng tiền bàn giao trừ 
                                             chiết khấu""", compute='_compute_gia_truoc_thue', store=True,
                                             readonly=True)
    bsd_tien_qsdd_moi = fields.Monetary(string="Giá trị QSDĐ",
                                        help="""Giá trị sử dụng đất: bằng QSDĐ/m2 nhân với diện tích sử dung""",
                                        readonly=True)
    bsd_tien_thue_moi = fields.Monetary(string="Tiền thuế",
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

    bsd_ltt_ids = fields.Many2many('bsd.lich_thanh_toan', relation='lich_moi_dkbg_rel', string="Lịch thanh toán",
                                   readonly=True)
    bsd_ly_do = fields.Char(string="Lý do không duyệt", readonly=True, tracking=2)
    company_id = fields.Many2one('res.company', string='Công ty', default=lambda self: self.env.company)
    currency_id = fields.Many2one(related="company_id.currency_id", string="Tiền tệ", readonly=True)
    bsd_thue_suat = fields.Float(string="Thuế suất", help="Thuế suất", readonly=True)
    bsd_tien_ps = fields.Monetary(string="Tiền phát sinh",
                                  help="Tiền phát sinh do hết đợt thanh toán", readonly=True)
    bsd_tien_vuot = fields.Monetary(string="Tiền vượt HĐ",
                                    help="Khi số tiền đã thu lớn hơn tiền thanh toán hợp đồng mới", readonly=True)
    bsd_da_co_lich = fields.Boolean(default=False)
    bsd_dot_ps_id = fields.Many2one('bsd.lich_thanh_toan', string="Đợt phát sinh")

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
            'name': 'Phụ lục thay đổi dkbg',
            'res_model': 'bsd.pl_dkbg',
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

    def action_chon_dkbg(self):
        if self.bsd_ltt_ids:
            raise UserError(_("Phụ lục đã có lịch thanh toán.\n"
                              "Vui lòng xóa lịch thanh toán trước khi chọn điều kiện bàn giao."))
        action = self.env.ref('bsd_dich_vu.bsd_wizard_pl_chon_dkbg_action').read()[0]
        return action

    def action_tao_lich_tt(self):
        # Xóa đợt chưa thanh toán để tạo lại lịch
        self.bsd_ltt_ids.filtered(lambda x: x.bsd_thanh_toan == 'chua_tt').unlink()
        # Xóa đợt phát sinh nếu có
        if self.bsd_dot_ps_id:
            self.bsd_dot_ps_id.unlink()
        # Xóa field tiền
        self.write({
            'bsd_tien_ps': 0,
            'bsd_tien_vuot': 0,
            'bsd_da_co_lich': True,
        })
        # Lấy các đợt đã thanh toán tiền của lịch cũ
        old_paid = self.bsd_ltt_ht_ids.filtered(lambda x: x.bsd_thanh_toan != 'chua_tt')
        for dot in old_paid:
            self.write({
                'bsd_ltt_ids': [(4, dot.id)]
            })
        # Lấy các đợt chưa thanh toán tiền của lịch cũ
        dot_chua_tt = self.bsd_ltt_ht_ids.filtered(lambda x: x.bsd_thanh_toan == 'chua_tt').sorted('bsd_stt')
        # Kiểm tra giá trị hợp đồng mới với tiền đã thanh toán
        # Nếu tiền thanh toán lớn hơn giá trị của hợp đồng mới thì tạo
        if self.bsd_tong_gia_moi - self.bsd_tien_pbt_moi <= self.bsd_tien_da_tt:
            # Ghi nhận số tiền vượt thanh toán
            self.write({'bsd_tien_vuot': self.bsd_tien_da_tt - (self.bsd_tong_gia_moi - self.bsd_tien_pbt_moi)})
            # Ghi nhận các đợt chưa thanh toán về 0
            # Copy các đợt chưa thanh toán
            for dot_tt in dot_chua_tt:
                dot_moi = dot_tt.copy()
                dot_moi.write({"bsd_tien_dot_tt": 0})
                self.write({
                    'bsd_ltt_ids': [(4, dot_moi.id)]
                })
        else:
            # Kiểm tra xem còn đợt chưa thanh toán hay ko
            if not dot_chua_tt:
                stt = len(self.bsd_ltt_ht_ids) + 1
                # Tạo đợt thanh toán với giá trị 0
                dot_phat_sinh = self.env['bsd.lich_thanh_toan'].create({
                                        'bsd_stt': stt,
                                        'bsd_ma_dtt': 'ĐPS',
                                        'bsd_ten_dtt': 'Đợt ' + str(stt),
                                        'bsd_tl_tt': 0,
                                        'bsd_tien_dot_tt': 0,
                                        'bsd_loai': 'dtt',
                                    }).id
                self.write({
                    'bsd_ltt_ids': [(4, dot_phat_sinh)],
                    'bsd_dot_ps_id': dot_phat_sinh,
                })
                # Ghi nhận tiền phát sinh do hết đợt chưa thanh toán
                self.write({'bsd_tien_ps': self.bsd_tong_gia_moi - self.bsd_tien_pbt_moi - self.bsd_tien_da_tt})
            # Nếu còn đợt chưa thanh toán
            else:
                # Tiền các đợt đã và đang thanh toán
                tien_da_va_dang_tt = sum(self.bsd_hd_ban_id.bsd_ltt_ids
                                         .filtered(lambda l: l.bsd_thanh_toan != 'chua_tt')
                                         .mapped('bsd_tien_dot_tt'))
                tong_tien_phai_tt = self.bsd_tong_gia_moi - self.bsd_tien_pbt_moi - tien_da_va_dang_tt
                # Kiểm tra tỷ lệ còn phải thanh toán
                tl_con_tt = 0
                for dot in dot_chua_tt:
                    tl_con_tt += dot.bsd_tl_tt
                # Kiểm tra số đợt còn lại
                so_dot_tt = len(dot_chua_tt)
                if so_dot_tt == 1:
                    dot_chua_tt_moi = dot_chua_tt.copy()
                    dot_chua_tt_moi.bsd_tien_dot_tt = tong_tien_phai_tt
                    self.write({
                        'bsd_ltt_ids': [(4, dot_chua_tt_moi.id)]
                    })
                else:
                    tien_da_chia_dot = 0
                    for dot in dot_chua_tt:
                        dot_moi = dot.copy()
                        # kiểm tra đợt cuối
                        if dot == dot_chua_tt[-1]:
                            dot_moi.bsd_tien_dot_tt = tong_tien_phai_tt - tien_da_chia_dot
                            self.write({
                                'bsd_ltt_ids': [(4, dot_moi.id)]
                            })
                            break
                        # Tính tiền đợt thanh toán khác cuối
                        tien_tt = (tong_tien_phai_tt * dot_moi.bsd_cs_tt_ct_id.bsd_tl_tt) / tl_con_tt
                        dot_moi.bsd_tien_dot_tt = tien_tt - (tien_tt % 1000)
                        tien_da_chia_dot += dot_moi.bsd_tien_dot_tt
                        self.write({
                            'bsd_ltt_ids': [(4, dot_moi.id)]
                        })

    # Xóa lịch thanh toán
    def action_xoa_lich_tt(self):
        # Xóa đợt chưa thanh toán
        self.bsd_ltt_ids.filtered(lambda x: x.bsd_thanh_toan == 'chua_tt').unlink()
        # Xóa đợt phát sinh nếu có
        if self.bsd_dot_ps_id:
            self.bsd_dot_ps_id.unlink()
        # bỏ liên kết với các đợt đã và đang thanh toán
        self.write({
            'bsd_ltt_ids': [(5, 0, 0)],
            'bsd_da_co_lich': False,
            'bsd_tien_ps': 0,
            'bsd_tien_vuot': 0,
        })

    # Ký phụ lục hợp đồng
    def action_ky_pl(self):
        if self.state == 'duyet':
            action = self.env.ref('bsd_dich_vu.bsd_wizard_ky_pl_action').read()[0]
            return action

    def thay_doi_dkbg(self):
        # Cập nhật lại điều kiện bàn giao của hợp đồng
        self.bsd_hd_ban_id.bsd_bg_ids.write({
            'state': 'huy',
        })
        for dk_bg in self.bsd_dkbg_moi_ids:
            if dk_bg.bsd_dk_tt == 'm2':
                tien_bg = dk_bg.bsd_gia_m2 * self.bsd_unit_id.bsd_dt_sd
            elif dk_bg.bsd_dk_tt == 'tien':
                tien_bg = dk_bg.bsd_tien
            else:
                tien_bg = dk_bg.bsd_ty_le * self.bsd_gia_ban_moi / 100
            self.env['bsd.ban_giao'].create({
                    'bsd_dk_bg_id': dk_bg.id,
                    'bsd_dk_tt': dk_bg.bsd_dk_tt,
                    'bsd_gia_m2': dk_bg.bsd_gia_m2,
                    'bsd_tien': dk_bg.bsd_tien,
                    'bsd_ty_le': dk_bg.bsd_ty_le,
                    'bsd_tien_bg': float_round(tien_bg, 0),
                    'bsd_pl_dkbg_id': self.id,
                    'bsd_hd_ban_id': self.bsd_hd_ban_id.id,
            })
        _logger.debug("debug1")
        # Cập nhật lại tỷ lệ chiết khấu của hợp đồng
        self.bsd_hd_ban_id.write({
            'bsd_tien_ck': self.bsd_tien_ck_moi,
        })
        _logger.debug("debug2")
        # Lấy các đợt chưa thanh toán ra khỏi hợp đồng
        self.bsd_ltt_ht_ids.filtered(lambda x: x.bsd_thanh_toan == 'chua_tt').write({'bsd_hd_ban_id': False})
        _logger.debug("debug3")
        # Kiểm tra nếu có tiền thu vượt hợp đồng
        if self.bsd_tien_vuot > 0:
            # Tạo thanh toán trả trước ứng với số tiền thu vượt
            self.env['bsd.phieu_thu'].create({
                'bsd_loai_pt': 'tra_truoc',
                'bsd_khach_hang_id': self.bsd_khach_hang_id.id,
                'bsd_pt_tt_id': self.env.ref('bsd_danh_muc.bsd_coa').id,
                'bsd_du_an_id': self.bsd_du_an_id.id,
                'bsd_tien_kh': self.bsd_tien_vuot,
            }).action_xac_nhan()
            # Gắn những đợt 0 đồng vào hợp đồng
            self.bsd_ltt_ids.write({'bsd_hd_ban_id': self.bsd_hd_ban_id.id})
            _logger.debug("debug4")
        elif self.bsd_tien_ps > 0:
            dot_ps = self.bsd_dot_ps_id
            dot_ps.write({'bsd_hd_ban_id': self.bsd_hd_ban_id.id})
            self.env['bsd.phi_ps'].create({
                'bsd_ten_ps': 'Phụ lục ' + self.bsd_ma,
                'bsd_du_an_id': self.bsd_du_an_id.id,
                'bsd_hd_ban_id': self.bsd_hd_ban_id.id,
                'bsd_dot_tt_id': dot_ps.id,
                'bsd_loai': 'pl_hd',
                'bsd_tien_ps': self.bsd_tien_ps
            })
            _logger.debug("debug5")
        # Thêm các đợt mới vào hợp đồng
        elif self.bsd_tien_vuot == 0 and self.bsd_tien_ps == 0:
            self.bsd_ltt_ids\
                .filtered(lambda x: x.bsd_thanh_toan == 'chua_tt')\
                .write({'bsd_hd_ban_id': self.bsd_hd_ban_id.id})
            # Lấy đợt thu phí quản lý bàn giao từ đợt cũ sang đợt mới
            dot_thu_pbt = self.bsd_ltt_ids.filtered(lambda x: x.bsd_tinh_pbt)
            dot_thu_pql = self.bsd_ltt_ids.filtered(lambda x: x.bsd_tinh_pql)
            self.bsd_hd_ban_id.bsd_dot_pbt_ids.write({'bsd_parent_id': dot_thu_pbt.id})
            self.bsd_hd_ban_id.bsd_dot_pql_ids.write({'bsd_parent_id': dot_thu_pql.id})
            _logger.debug("debug6")

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
            raise UserError(_('Dự án chưa có quy định mã phụ lục thay đổi điều kiện bàn giao.\n'
                              'Vui lòng kiểm tra lại thông tin.'))
        vals['bsd_ma'] = sequence.next_by_id()
        res = super(BsdPLDKBG, self).create(vals)
        res.write({
            'bsd_gia_ban_moi': res.bsd_gia_ban_ht,
            'bsd_tien_ck_moi': res.bsd_tien_ck_ht,
            'bsd_tien_qsdd_moi': res.bsd_tien_qsdd_ht,
            'bsd_tien_pbt_moi': res.bsd_tien_pbt_ht,
        })
        return res


class BsdBanGiao(models.Model):
    _inherit = 'bsd.ban_giao'

    bsd_pl_dkbg_id = fields.Many2one('bsd.pl_dkbg', string="Phụ lục", readonly=True)