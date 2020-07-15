# -*- coding:utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError


class BsdChuyenNhuong(models.Model):
    _name = 'bsd.hd_ban_cn'
    _description = " Chuyển nhượng hợp đồng"
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _rec_name = 'bsd_ten_cn'

    bsd_ma_cn = fields.Char(string="Mã chứng từ", help="Mã chứng từ chuyển nhượng", required=True, readonly=True,
                            copy=False, default='/')

    _sql_constraints = [
        ('bsd_ma_cn_unique', 'unique (bsd_ma_cn)',
         'Mã chứng từ chuyển nhượng đã tồn tại !')
    ]
    bsd_ten_cn = fields.Char(string="Tiêu đề", help="Tiêu đề", required=True)
    bsd_ngay_cn = fields.Datetime(string="Ngày chứng từ", required=True, default=lambda self: fields.Datetime.now())
    bsd_loai = fields.Selection([('cty', 'Tại công ty'), ('vpcn', 'Tại văn phòng công chứng')],
                                string="Loại chuyển nhượng", required=True, default='cty')
    bsd_du_an_id = fields.Many2one('bsd.du_an', string="Dự án", required=True)
    bsd_hd_ban_id = fields.Many2one('bsd.hd_ban', string="Hợp đồng", required=True)
    bsd_unit_id = fields.Many2one(related='bsd_hd_ban_id.bsd_unit_id')
    bsd_hd_ban_state = fields.Selection(related="bsd_hd_ban_id.state")
    bsd_ngay_hl_cn = fields.Datetime(string="Hiệu lực CN", readonly=True,
                                     help="""Hiệu lực chuyển nhượng được tính là sau 14 ngày kể từ 
                                             khi chọn Khác hàng được chuyển nhượng""")
    bsd_ngay_kt_xn = fields.Datetime(string="Xác nhận LKTT", readonly=True,
                                     help="""Ngày kế toán xác nhận hoàn thành lũy kế thanh 
                                                                    toán cho khách hàng""")
    bsd_ngay_in_vb = fields.Datetime(string="Ngày in VBCN", readonly=True,
                                     help="Ngày in Văn bản chuyển nhượng/ Xác "
                                          "nhận cho phép chuyển nhượng")
    bsd_ngay_in_xn_vb = fields.Datetime(string="Ngày xác nhận CN", readonly=True,
                                        help="""Ngày in xác nhận văn bản chuyển nhượng""")
    bsd_ngay_duyet = fields.Datetime(string="Ngày duyệt", help="Ngày duyệt xác nhận chuyển nhượng", readonly=True)
    bsd_nguoi_duyet_id = fields.Many2one("res.users", string="Người duyệt",
                                         help="Người duyệt xác nhận chuyển nhượng", readonly=True)
    bsd_khach_hang_id = fields.Many2one("res.partner", string="Khách hàng hiện tại", reaonly=True,
                                        required=True, help="Khách hàng có nhu cầu chuyển nhượng")
    bsd_co_dsh_ht = fields.Boolean(string="Đồng sở hữu hiện tại")
    bsd_dsh_ht_ids = fields.Many2many('res.partner', relation="bsd_hd_ban_cn_kh_ht",
                                      string="Danh sách đồng sở hữu hiện tại")

    bsd_kh_moi_id = fields.Many2one('res.partner', string="Khách hàng mới", help="Khách hàng được chuyển nhượng")
    bsd_co_dsh_moi = fields.Boolean(string="Đồng sở hữu mới")
    bsd_dsh_moi_ids = fields.Many2many('res.partner',
                                       relation="bsd_hd_ban_cn_kh_moi",
                                       string="Danh sách đồng sở hữu mới")
    bsd_so_cch = fields.Char(string="Số công chứng", help="Số công chứng")
    bsd_noi_cch = fields.Many2one('res.country.state', string="Nơi công chứng")
    bsd_ngay_cch = fields.Date(string="Ngày công chứng", help="Ngày công chứng")
    bsd_so_tb = fields.Char(string="Số thông báo", help="Số thông báo")
    bsd_noi_tb = fields.Many2one('res.country.state', string="Nơi thông báo", help="Nơi thông báo")
    bsd_ngay_tb = fields.Date(string="Ngày thông báo", help="Ngày thông báo")
    bsd_ngay_cn_tt = fields.Datetime(string="Ngày cập nhật", help="Ngày cập nhật thông tin công chứng")
    state = fields.Selection([('nhap', 'Nháp'), ('xac_nhan', 'Xác nhận'), ('duyet', 'Duyệt'), ('huy', 'Hủy')],
                             string="Trạng thái", default='nhap', required=True, readonly=True, tracking=1)

    @api.onchange('bsd_hd_ban_id')
    def _onchange_hd_ban(self):
        self.bsd_khach_hang_id = self.bsd_hd_ban_id.bsd_khach_hang_id
        if self.bsd_hd_ban_id.bsd_dong_sh_ids:
            self.bsd_co_dsh_ht = True
            self.bsd_dsh_ht_ids = self.bsd_hd_ban_id.bsd_dong_sh_ids.mapped('bsd_dong_sh_id')

    # DV.09.01 Xác nhận
    def action_xac_nhan(self):
        self.write({
            'state': 'xac_nhan'
        })

    # DV.09.02 Xác nhận lũy kế thanh toán
    def action_xac_nhan_ttlk(self):
        self.write({
            'bsd_ngay_kt_xn': fields.Datetime.now()
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

    # DV.09.03 In chứng từ chuyển nhượng
    def action_in_cn(self):
        return self.env.ref('bsd_dich_vu.bsd_hd_ban_cn_report_action').read()[0]

    # DV.09.05 Duyệt chuyển nhượng
    def action_duyet(self):
        # Kiểm tra trạng thái của hợp đồng
        if self.bsd_hd_ban_id.state in ['thanh_ly', 'huy']:
            raise UserError("Hợp đồng đã bị thanh lý. Vui lòng kiểm tra lại thông tin hợp đồng")
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
                    'bsd_dong_sh_id': moi.id,
                    'bsd_hd_ban_id': self.bsd_hd_ban_id.id,
                    'bsd_hd_ban_cn_id': self.id,
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
                    'bsd_dong_sh_id': moi.id,
                    'bsd_hd_ban_id': self.bsd_hd_ban_id.id,
                    'bsd_hd_ban_cn_id': self.id,
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

    # DV.09.07 Hủy chuyển nhượng
    def action_huy(self):
        if self.state in ['nhap', 'xac_nhan']:
            self.write({
                'state': 'huy'
            })

    # DV.09.08 Kiểm tra công nợ khách hàng
    @api.constrains('bsd_hd_ban_id')
    def _constrains_hd_ban(self):
        dot_dang_tt = self.bsd_hd_ban_id.bsd_ltt_ids.filtered(lambda x: x.bsd_thanh_toan == 'dang_tt')
        if dot_dang_tt:
            raise UserError("Hợp đồng chưa hoàn tất công nợ. Vui lòng kiểm tra lại thông tin hợp đồng")

    @api.model
    def create(self, vals):
        sequence = False
        if 'bsd_du_an_id' in vals:
            du_an = self.env['bsd.du_an'].browse(vals['bsd_du_an_id'])
            sequence = du_an.get_ma_bo_cn(loai_cn=self._name)
        if not sequence:
            raise UserError(_('Dự án chưa có mã chuyển nhượng hợp đồng'))
        vals['bsd_ma_cn'] = sequence.next_by_id()
        res = super(BsdChuyenNhuong, self).create(vals)

        if res.bsd_hd_ban_id.bsd_dong_sh_ids:
            res.bsd_co_dsh_ht = True
            res.write({
                'bsd_dsh_ht_ids': [(6, 0, res.bsd_hd_ban_id.bsd_dong_sh_ids.mapped('bsd_dong_sh_id').ids)]
            })
        return res