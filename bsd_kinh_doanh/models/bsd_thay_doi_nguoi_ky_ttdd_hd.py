# -*- conding:utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError
import logging
_logger = logging.getLogger(__name__)


class BsdThayDoiNguoiKy(models.Model):
    _name = 'bsd.dat_coc.chuyen_dd'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _rec_name = 'bsd_ma'
    _description = 'Phiếu chuyển người đại diện ký thỏa thuận đặt cọc, hợp đồng mua bán'

    bsd_ma = fields.Char(string="Mã", help="Mã phiếu chuyển người đại diện ký TTĐC/HĐB", required=True, readonly=True, copy=False,
                         default='/')
    _sql_constraints = [
        ('bsd_ma_unique', 'unique (bsd_ma)',
         'Mã phiếu chuyển người đại diện đã tồn tại !')]
    bsd_ngay = fields.Date(string="Ngày", help="Ngày tạo phiếu chuyển đại diện", default=lambda self: fields.Date.today(),
                                  readonly=True,
                                  states={'nhap': [('readonly', False)]})
    bsd_tieu_de = fields.Char(string="Tiêu đề", help="Tiêu đề phiếu thay đổi đại diện ký", required=True,
                              readonly=True, states={'nhap': [('readonly', False)]})
    bsd_kh_ht_id = fields.Many2one("res.partner", string="Người ký hiện tại", help="Người đại diện ký hiên tại",
                                   required=True,
                                   readonly=True,
                                   states={'nhap': [('readonly', False)]})
    bsd_dsh_ht_ids = fields.Many2many("bsd.dong_so_huu",
                                      relation="bsd_dsh_ht_rel",
                                      column2="bsd_dong_sh_id",
                                      column1="bsd_chuyen_dd_id",
                                      string="Đồng sở hữu hiện tại", readonly=True)

    bsd_dat_coc_id = fields.Many2one('bsd.dat_coc', string="Đặt cọc", help="Đặt cọc",
                                     readonly=True,
                                     states={'nhap': [('readonly', False)]})
    bsd_du_an_id = fields.Many2one("bsd.du_an", string="Dự án", help="Dự án", required=True,
                                   readonly=True,
                                   states={'nhap': [('readonly', False)]})
    bsd_unit_id = fields.Many2one('product.product', string="Sản phẩm", help="Sản phẩm", required=True,
                                  readonly=True,
                                  states={'nhap': [('readonly', False)]})

    @api.onchange('bsd_dat_coc_id')
    def _onchange_dat_coc(self):
        self.bsd_unit_id = self.bsd_dat_coc_id.bsd_unit_id
        self.bsd_du_an_id = self.bsd_dat_coc_id.bsd_du_an_id
        self.bsd_kh_ht_id = self.bsd_dat_coc_id.bsd_nguoi_dd_id
        self.bsd_dsh_ht_ids = [(6, 0, self.bsd_dat_coc_id.bsd_dong_sh_ids.ids)]

    bsd_kh_moi_id = fields.Many2one('res.partner', string="Người ký mới", help="Người đại diện ký mới",
                                    required=True,
                                    readonly=True,
                                    states={'nhap': [('readonly', False)]})
    bsd_co_dsh_moi = fields.Boolean(string="Thay đổi đồng sở hữu", default=False)
    bsd_dsh_moi_ids = fields.One2many("bsd.dong_so_huu", 'bsd_chuyen_dd_id',
                                      string="Đồng sở hữu mới", help="Danh sách người đồng sở hữu mới")

    bsd_dien_giai = fields.Char(string="Diễn giải", help="Diễn giải",
                                readonly=True,
                                states={'nhap': [('readonly', False)]})
    bsd_ly_do = fields.Char(string="Lý do", readonly=True, tracking=2)

    state = fields.Selection([('nhap', 'Nháp'), ('xac_nhan', 'Xác nhận'),
                              ('da_duyet', 'Đã duyệt'), ('huy', 'Hủy')], string="Trạng thái", help="Trạng thái",
                             required=True, default='nhap', tracking=1)
    bsd_nguoi_duyet_id = fields.Many2one('res.users', string="Người duyệt", readonly=True)
    bsd_ngay_duyet = fields.Datetime(string="Ngày duyệt", readonly=True)

    @api.constrains('bsd_kh_moi_id', 'bsd_kh_ht_id')
    def _constrains_kh_moi(self):
        if self.bsd_kh_ht_id == self.bsd_kh_moi_id:
            raise UserError(_('Người đại diện ký TTĐC/HĐ mới không được trùng với người hiện tại.\n'
                              'Vui lòng kiểm tra lại thông tin.'))

    # KD Xác nhận phiếu chuyển người đại diện đặt cọc
    def action_xac_nhan(self):
        # Kiểm tra đặt cọc đã tạo hợp đồng chưa và đặt cọc còn hiệu lực không
        if self.bsd_dat_coc_id.state not in ['da_tc', 'dat_coc']:
            raise UserError("Đặt cọc đã hết hiệu lực.\nVui lòng kiểm tra lại thông tin.")
        hd_ban = self.env['bsd.hd_ban'].search([('bsd_dat_coc_id', '=', self.bsd_dat_coc_id.id)])
        if hd_ban:
            raise UserError(_("Đặt cọc đã tạo hợp đồng.\nVui lòng kiểm tra lại thông tin."))
        if self.state == 'nhap':
            self.write({
                'state': 'xac_nhan',
            })

    # KD.05.07.02 Duyệt chuyển tên khách hàng giữ chỗ
    def action_duyet(self):
        # Kiểm tra đặt cọc đã tạo hợp đồng chưa và đặt cọc còn hiệu lực không
        if self.bsd_dat_coc_id.state not in ['da_tc', 'dat_coc']:
            raise UserError("Đặt cọc đã hết hiệu lực.\nVui lòng kiểm tra lại thông tin.")
        hd_ban = self.env['bsd.hd_ban'].search([('bsd_dat_coc_id', '=', self.bsd_dat_coc_id.id)])
        if hd_ban:
            raise UserError(_("Đặt cọc đã tạo hợp đồng.\nVui lòng kiểm tra lại thông tin."))
        if self.state == 'xac_nhan':
            self.write({
                'state': 'da_duyet',
                'bsd_nguoi_duyet_id': self.env.uid,
                'bsd_ngay_duyet': fields.Datetime.now(),
            })
        self.bsd_dat_coc_id.write({
            'bsd_nguoi_dd_id': self.bsd_kh_moi_id.id,
            'bsd_dong_sh_ids': [(6, 0, self.bsd_dsh_moi_ids.ids)]
        })

    # KD.05.07.03 Từ chối yêu cầu thay đổi
    def action_khong_duyet(self):
        action = self.env.ref('bsd_kinh_doanh.bsd_wizard_chuyen_dd_action').read()[0]
        return action

    # KD.05.07.04 Hủy chuyển tên khách hàng giữ chỗ
    def action_huy(self):
        if self.state in ['nhap', 'xac_nhan']:
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
            raise UserError(_('Dự án chưa có mã phiếu thay đổi người đại diện ký TTĐC/HĐMB.'))
        vals['bsd_ma'] = sequence.next_by_id()
        return super(BsdThayDoiNguoiKy, self).create(vals)