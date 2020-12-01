# -*- coding:utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError
import logging
import datetime
_logger = logging.getLogger(__name__)


class BsdChuyenNhuong(models.Model):
    _name = 'bsd.hd_ban_cn'
    _description = " Chuyển nhượng hợp đồng"
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _rec_name = 'bsd_ten_cn'

    bsd_ma_cn = fields.Char(string="Mã", help="Mã chứng từ chuyển nhượng", required=True, readonly=True,
                            copy=False, default='/')

    _sql_constraints = [
        ('bsd_ma_cn_unique', 'unique (bsd_ma_cn)',
         'Mã chứng từ chuyển nhượng đã tồn tại !')
    ]
    bsd_ten_cn = fields.Char(string="Tiêu đề", help="Tiêu đề", required=True,
                             readonly=True,
                             states={'nhap': [('readonly', False)]})
    bsd_ngay_cn = fields.Datetime(string="Ngày", required=True, default=lambda self: fields.Datetime.now(),
                                  readonly=True,
                                  states={'nhap': [('readonly', False)]})
    bsd_loai = fields.Selection([('cty', 'Tại công ty'), ('vpcn', 'Tại văn phòng công chứng')],
                                string="Loại CN", required=True, default='cty',
                                readonly=True,
                                states={'nhap': [('readonly', False)]})
    bsd_du_an_id = fields.Many2one('bsd.du_an', string="Dự án", required=True,
                                   readonly=True,
                                   states={'nhap': [('readonly', False)]})
    bsd_hd_ban_id = fields.Many2one('bsd.hd_ban', string="Hợp đồng", required=True,
                                    readonly=True,
                                    states={'nhap': [('readonly', False)]})
    bsd_unit_id = fields.Many2one(related='bsd_hd_ban_id.bsd_unit_id', store=True)
    bsd_hd_ban_state = fields.Selection([
                                      ('da_ky', 'Đã ký HĐ'),
                                      ('dang_tt', 'Đang thanh toán'),
                                      ('du_dkbg', 'Đủ ĐKBG'),
                                      ('da_bg', 'Đã bàn giao'),
                                      ('ht_tt', 'Hoàn tất thanh toán')],
        string="Trạng thái HĐ", readonly=True)
    bsd_ngay_hl_cn = fields.Date(string="Hiệu lực CN", readonly=True,
                                 help="""Hiệu lực chuyển nhượng được tính là sau 14 ngày kể từ 
                                         khi chọn Khác hàng được chuyển nhượng""")
    bsd_ngay_kt_xn = fields.Date(string="Xác nhận LKTT", readonly=True,
                                 help="""Ngày kế toán xác nhận hoàn thành lũy kế thanh 
                                                                    toán cho khách hàng""")
    bsd_ngay_in_vb = fields.Date(string="Ngày in VBCN", readonly=True,
                                 help="Ngày in Văn bản chuyển nhượng/ Xác "
                                      "nhận cho phép chuyển nhượng")
    bsd_ngay_in_xn_vb = fields.Date(string="Ngày xác nhận CN", readonly=True,
                                        help="""Ngày in xác nhận văn bản chuyển nhượng""")
    bsd_ngay_duyet = fields.Date(string="Ngày duyệt", help="Ngày duyệt xác nhận chuyển nhượng", readonly=True)
    bsd_nguoi_duyet_id = fields.Many2one("res.users", string="Người duyệt",
                                         help="Người duyệt xác nhận chuyển nhượng", readonly=True)
    bsd_khach_hang_id = fields.Many2one("res.partner", string="Khách hàng hiện tại", reaonly=True,
                                        required=True, help="Khách hàng có nhu cầu chuyển nhượng")
    bsd_co_dsh_ht = fields.Boolean(string="Đồng sở hữu hiện tại")
    bsd_dsh_ht_ids = fields.One2many('bsd.cn_dsh_cu', 'bsd_cn_id',
                                      string="Đồng sở hữu hiện tại")

    bsd_kh_moi_id = fields.Many2one('res.partner', string="Khách hàng mới", help="Khách hàng được chuyển nhượng",
                                    readonly=True,
                                    states={'nhap': [('readonly', False)], 'da_xn_ttlk': [('readonly', False)]})
    bsd_co_dsh_moi = fields.Boolean(string="Đồng sở hữu mới",
                                    readonly=True,
                                    states={'nhap': [('readonly', False)], 'da_xn_ttlk': [('readonly', False)]})
    bsd_dsh_moi_ids = fields.One2many('bsd.cn_dsh_moi', 'bsd_cn_id',
                                      string="Đồng sở hữu mới",
                                      readonly=True,
                                      states={'nhap': [('readonly', False)], 'da_xn_ttlk': [('readonly', False)]})
    bsd_so_cch = fields.Char(string="Số công chứng", help="Số công chứng", readonly=True,
                             states={'nhap': [('readonly', False)], 'da_xn_ttlk': [('readonly', False)]})
    bsd_noi_cch = fields.Char(string="Nơi công chứng", readonly=True,
                              states={'nhap': [('readonly', False)], 'da_xn_ttlk': [('readonly', False)]})
    bsd_ngay_cch = fields.Date(string="Ngày công chứng", help="Ngày công chứng", readonly=True,
                               states={'nhap': [('readonly', False)], 'da_xn_ttlk': [('readonly', False)]})
    bsd_so_tb = fields.Char(string="Số thông báo", help="Số thông báo", readonly=True,
                            states={'nhap': [('readonly', False)], 'da_xn_ttlk': [('readonly', False)]})
    bsd_noi_tb = fields.Char(string="Nơi thông báo", help="Nơi thông báo", readonly=True,
                             states={'nhap': [('readonly', False)], 'da_xn_ttlk': [('readonly', False)]})
    bsd_ngay_tb = fields.Date(string="Ngày thông báo", help="Ngày thông báo", readonly=True,
                              states={'nhap': [('readonly', False)], 'da_xn_ttlk': [('readonly', False)]})
    bsd_gcn_nt = fields.Char(string="GCN.Nộp thuế", help="Giấy chứng nhận đã nộp thuế", readonly=True,
                             states={'nhap': [('readonly', False)], 'da_xn_ttlk': [('readonly', False)]})
    bsd_giay_cn = fields.Char(string="GCN.Chủ đầu tư", help="Giấy chứng nhận chủ đầu tư", readonly=True,
                              states={'nhap': [('readonly', False)], 'da_xn_ttlk': [('readonly', False)]})
    bsd_tt_cch = fields.Char(string="Thông tin công chứng", readonly=True,
                             states={'nhap': [('readonly', False)], 'da_xn_ttlk': [('readonly', False)]})
    state = fields.Selection([('nhap', 'Nháp'), ('cho_xn_ttlk', 'Chờ xác nhận TTLK'),
                              ('da_xn_ttlk', 'Đã xác nhận TTLK'),
                              ('xac_nhan', 'Xác nhận'),
                              ('duyet', 'Duyệt'),
                              ('huy', 'Hủy')],
                             string="Trạng thái", default='nhap', required=True, readonly=True, tracking=1)
    bsd_ly_do = fields.Char(string="Lý do", readonly=True, tracking=2)

    @api.onchange('bsd_hd_ban_id')
    def _onchange_hd_ban(self):
        self.bsd_khach_hang_id = self.bsd_hd_ban_id.bsd_khach_hang_id
        self.bsd_hd_ban_state = self.bsd_hd_ban_id.state
        if self.bsd_hd_ban_id.bsd_dong_sh_ids:
            self.bsd_co_dsh_ht = True

    # DV.09.01 Xác nhận
    def action_xac_nhan(self):
        self.write({
            'state': 'cho_xn_ttlk'
        })

    # DV.09.02 Xác nhận lũy kế thanh toán
    def action_xac_nhan_ttlk(self):
        self.write({
            'bsd_ngay_kt_xn': fields.Date.today(),
            'state': 'da_xn_ttlk'
        })
        message_id = self.env['message.wizard'].create(
            {'message': _("Vui lòng đính kèm Thư xác nhận thanh toán lũy kế và "
                          "Biên bản xác nhận bàn giao hóa đơn vào hệ thống")})
        return {
            'name': _('Thông báo'),
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            'res_model': 'message.wizard',
            'res_id': message_id.id,
            'target': 'new'
        }

    def action_xac_nhan_tt(self):
        if self.state == 'da_xn_ttlk':
            self.write({
                'state': 'xac_nhan'
            })
        if not self.bsd_kh_moi_id:
            raise UserError("Vui lòng nhập khách hàng được chuyển nhượng.")
        else:
            self.bsd_ngay_hl_cn = fields.datetime.now() + datetime.timedelta(days=14)

    # DV.09.03 In chứng từ chuyển nhượng
    def action_in_cn(self):
        return self.env.ref('bsd_dich_vu.bsd_hd_ban_cn_report_action').read()[0]

    # DV.09.05 Duyệt chuyển nhượng
    def action_duyet(self):
        # Kiểm tra trạng thái của hợp đồng
        if self.bsd_hd_ban_id.state in ['thanh_ly', 'huy']:
            raise UserError("Hợp đồng đã bị thanh lý. Vui lòng kiểm tra lại thông tin hợp đồng.")
        # Cập nhật trạng thái vào chuyến nhượng
        self.write({
            'state': 'duyet',
            'bsd_nguoi_duyet_id': self.env.uid,
            'bsd_ngay_duyet': fields.Datetime.now(),
        })
        # Cập nhật thông tin hợp đồng
        self.bsd_hd_ban_id.write({
            'bsd_khach_hang_id': self.bsd_kh_moi_id.id,
        })
        # Cập nhật danh sách đồng sở hữu
        old_dsh = self.bsd_hd_ban_id.bsd_dong_sh_ids
        new_dsh = self.env['bsd.dong_so_huu']
        if not old_dsh:
            for moi in self.bsd_dsh_moi_ids:
                new_dsh.create({
                    'bsd_dong_sh_id': moi.bsd_dong_sh_id.id,
                    'bsd_hd_ban_id': self.bsd_hd_ban_id.id,
                    'bsd_hd_ban_cn_id': self.id,
                    'bsd_quan_he': moi.bsd_quan_he,
                    'bsd_lan_td': 1,
                    'state': 'active',
                })
        else:
            old_dsh_active = old_dsh.filtered(lambda o: o.state == 'active')
            if old_dsh_active:
                old_dsh_active.write({
                    'state': 'inactive'
                })
            lan_td = max(old_dsh.mapped('bsd_lan_td'))
            for moi in self.bsd_dsh_moi_ids:
                new_dsh.create({
                    'bsd_dong_sh_id': moi.bsd_dong_sh_id.id,
                    'bsd_hd_ban_id': self.bsd_hd_ban_id.id,
                    'bsd_hd_ban_cn_id': self.id,
                    'bsd_quan_he': moi.bsd_quan_he,
                    'bsd_lan_td': lan_td + 1,
                    'state': 'active',
                })
        # DV.09.09 - Xử lý công nợ khách hàng Chuyển nhượng HĐ
        # lấy các đợt đã thanh toán của hợp đồng
        dot_tt_ids = self.bsd_hd_ban_id.bsd_ltt_ids.filtered(lambda d: d.bsd_thanh_toan == 'chua_tt')
        cong_no_kh_cu = self.env['bsd.cong_no'].search([('bsd_hd_ban_id', '=', self.bsd_hd_ban_id.id),
                                                        ('bsd_dot_tt_id', 'in', dot_tt_ids.ids),
                                                        ('bsd_khach_hang_id', '=', self.bsd_khach_hang_id.id)])
        # hủy công nợ của khách hàng cũ
        cong_no_kh_cu.write({'state': 'huy'})
        # tạo công nợ cho khách hàng mới
        for dot_tt in dot_tt_ids:
            self.env['bsd.cong_no'].create({
                'bsd_chung_tu': dot_tt.bsd_ten_dtt,
                'bsd_ngay': dot_tt.bsd_ngay_hh_tt,
                'bsd_khach_hang_id': self.bsd_kh_moi_id.id,
                'bsd_du_an_id': self.bsd_du_an_id.id,
                'bsd_ps_tang': dot_tt.bsd_tien_dot_tt,
                'bsd_ps_giam': 0,
                'bsd_loai_ct': 'dot_tt',
                'bsd_phat_sinh': 'tang',
                'bsd_hd_ban_id': self.bsd_hd_ban_id.id,
                'bsd_dot_tt_id': dot_tt.id,
                'state': 'da_gs',
            })

    # DV.09.06 Không duyệt chuyển nhượng
    def action_khong_duyet(self):
        action = self.env.ref('bsd_dich_vu.bsd_wizard_hd_ban_cn_action').read()[0]
        return action

    # DV.09.07 Hủy chuyển nhượng
    def action_huy(self):
        if self.state in ['nhap', 'xac_nhan']:
            self.write({
                'state': 'huy'
            })

    # DV.09.08 Kiểm tra hợp đồng
    @api.constrains('bsd_hd_ban_id')
    def _constrains_hd_ban(self):
        dot_dang_tt = self.bsd_hd_ban_id.bsd_ltt_ids.filtered(lambda x: x.bsd_thanh_toan == 'dang_tt')
        if dot_dang_tt:
            raise UserError("Hợp đồng chưa hoàn tất công nợ.\nVui lòng kiểm tra lại thông tin hợp đồng.")
        # Kiểm tra sản phẩm có đang thế chấp ngân hàng ko
        if self.bsd_hd_ban_id.bsd_unit_id.bsd_tt_vay == '1':
            raise UserError("Hợp đồng đã có thế chấp ngân hàng.\nVui lòng kiểm tra lại thông tin hợp đồng.")
        # Kiểm tra sản phẩm đã gửi thông tin làm sổ hồng chưa
        if self.bsd_hd_ban_id.bsd_unit_id.bsd_xn_du_hs == '1':
            raise UserError("Hợp đồng thông báo hợp đồng đang gửi thông tin là sổ hồng."
                            "\nVui lòng kiểm tra lại thông tin hợp đồng")

    @api.constrains('bsd_kh_moi_id')
    def _constrains_kh_moi(self):
        if self.bsd_kh_moi_id == self.bsd_khach_hang_id:
            raise UserError(_("Khách hàng mới trùng mới khách hàng hiện tại."
                              "\nVui lòng kiểm tra lại thông tin."))

    @api.constrains('bsd_dsh_moi_ids')
    def _constrains_dsh(self):
        for each in self:
            record = each.bsd_dsh_moi_ids
            dsh = each.bsd_dsh_moi_ids.mapped('bsd_dong_sh_id')
            if len(record) > len(dsh):
                raise UserError("Trùng khách hàng đồng sở hữu.\nVui lòng kiểm tra lại thông tin.")
    @api.model
    def create(self, vals):
        sequence = False
        if 'bsd_du_an_id' in vals:
            du_an = self.env['bsd.du_an'].browse(vals['bsd_du_an_id'])
            sequence = du_an.get_ma_bo_cn(loai_cn=self._name)
        if not sequence:
            raise UserError(_('Dự án chưa có mã chuyển nhượng hợp đồng.'))
        vals['bsd_ma_cn'] = sequence.next_by_id()
        res = super(BsdChuyenNhuong, self).create(vals)

        ids_dsh = res.bsd_hd_ban_id.bsd_dong_sh_ids.filtered(lambda x: x.state == 'active')
        for id_dsh in ids_dsh:
            res.bsd_dsh_ht_ids.create({
                'bsd_dong_sh_id': id_dsh.bsd_dong_sh_id.id,
                'bsd_cn_id': res.id,
                'bsd_quan_he': id_dsh.bsd_quan_he,
            })
        return res


class BsdCNDSHMoi(models.Model):
    _name = 'bsd.cn_dsh_moi'
    _description = "Danh sách đồng sở hữu mới"

    bsd_dong_sh_id = fields.Many2one('res.partner', string="Đồng sở hữu", required=True)
    mobile = fields.Char(related='bsd_dong_sh_id.mobile', string="Di động")
    email = fields.Char(related='bsd_dong_sh_id.email', string="Email")
    bsd_quan_he = fields.Selection([('vo', 'Vợ'),
                                    ('chong', 'Chồng'),
                                    ('con', 'Con'),
                                    ('chau', 'Cháu'),
                                    ('nguoi_than', 'Người thân'),
                                    ('ban', 'Bạn'),
                                    ('khac', 'Khác')
                                    ], string="Mối quan hệ", required=True)
    bsd_cn_id = fields.Many2one('bsd.hd_ban_cn',
                                string="Chuyển nhượng HĐ",
                                ondelete="CASCADE",
                                help="Mã chuyển nhượng hợp đồng")


class BsdCNDSHCu(models.Model):
    _name = 'bsd.cn_dsh_cu'
    _description = "Danh sách đồng sở hữu cũ"

    bsd_dong_sh_id = fields.Many2one('res.partner', string="Đồng sở hữu", required=True)
    mobile = fields.Char(related='bsd_dong_sh_id.mobile', string="Di động")
    email = fields.Char(related='bsd_dong_sh_id.email', string="Email")
    bsd_quan_he = fields.Selection([('vo', 'Vợ'),
                                    ('chong', 'Chồng'),
                                    ('con', 'Con'),
                                    ('chau', 'Cháu'),
                                    ('nguoi_than', 'Người thân'),
                                    ('ban', 'Bạn'),
                                    ('khac', 'Khác')
                                    ], string="Mối quan hệ", required=True)
    bsd_cn_id = fields.Many2one('bsd.hd_ban_cn',
                                string="Chuyển nhượng HĐ",
                                ondelete="CASCADE",
                                help="Mã chuyển nhượng hợp đồng")