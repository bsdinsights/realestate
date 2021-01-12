# -*- conding:utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError
import logging
_logger = logging.getLogger(__name__)


class BsdThayDoiThongTinDatCoc(models.Model):
    _name = 'bsd.dat_coc.td_tt'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _rec_name = 'bsd_ma'
    _description = 'Phiếu thay đổi thông tin đặt cọc'

    bsd_ma = fields.Char(string="Mã", help="Mã phiếu thay đổi thông tin đặt cọc",
                         required=True, readonly=True, copy=False,
                         default='/')
    _sql_constraints = [
        ('bsd_ma_unique', 'unique (bsd_ma)',
         'Mã phiếu chuyển người đại diện đã tồn tại !')]
    bsd_ngay = fields.Date(string="Ngày", help="Ngày tạo phiếu thay đổi thông tin đặt cọc", default=lambda self: fields.Date.today(),
                                  readonly=True,
                                  states={'nhap': [('readonly', False)]})
    bsd_tieu_de = fields.Char(string="Tiêu đề", help="Tiêu đề phiếu thay đổi thông tin đặt cọc", required=True,
                              readonly=True, states={'nhap': [('readonly', False)]})
    bsd_dien_giai = fields.Char(string="Diễn giải", help="Diễn giải",
                                readonly=True,
                                states={'nhap': [('readonly', False)]})
    bsd_dat_coc_id = fields.Many2one('bsd.dat_coc', string="Đặt cọc", help="Đặt cọc",
                                     readonly=True,
                                     states={'nhap': [('readonly', False)]})
    bsd_du_an_id = fields.Many2one("bsd.du_an", string="Dự án", help="Dự án", required=True,
                                   readonly=True,
                                   states={'nhap': [('readonly', False)]})
    bsd_dot_mb_id = fields.Many2one('bsd.dot_mb', string="Đợt mở bán", readonly=True)
    bsd_unit_id = fields.Many2one('product.product', string="Sản phẩm", help="Sản phẩm", required=True,
                                  readonly=True,
                                  states={'nhap': [('readonly', False)]})
    bsd_khach_hang_id = fields.Many2one('res.partner', string="Khách hàng", help="Khách hàng", required=True,
                                        readonly=True,
                                        states={'nhap': [('readonly', False)]})
    bsd_loai_td = fields.Selection([('dong_sh', 'Đồng sở hữu'),
                                    ('khuyen_mai', 'Khuyến mãi'),
                                    ('pt_tt', "Phương thức thanh toán"),
                                    ('dk_bg', "Điều kiện bàn giao"),
                                    ('ck_tm', "Chiết khấu thương mại")], string="Loại", default='dong_sh',
                                   required=True, readonly=True, states={'nhap': [('readonly', False)]})
    bsd_dsh_ht_ids = fields.Many2many('bsd.dong_so_huu', string="Đồng sở hữu ht", readonly=True)
    bsd_dsh_moi_ids = fields.One2many('bsd.dong_so_huu', 'bsd_td_tt_id', string="Đồng sở hữu mới", readonly=True,
                                      states={'xac_nhan': [('readonly', False)]})
    bsd_km_ht_ids = fields.Many2many('bsd.bao_gia_km', string="Khuyến mãi hiện tại", readonly=True)
    bsd_km_moi_ids = fields.One2many('bsd.bao_gia_km', 'bsd_td_tt_id', string="Khuyến mãi mới", readonly=True,
                                     states={'xac_nhan': [('readonly', False)]})

    @api.onchange('bsd_dat_coc_id', 'bsd_loai_td')
    def _onchange_dat_coc(self):
        self.bsd_unit_id = self.bsd_dat_coc_id.bsd_unit_id
        self.bsd_du_an_id = self.bsd_dat_coc_id.bsd_du_an_id
        self.bsd_khach_hang_id = self.bsd_dat_coc_id.bsd_khach_hang_id
        self.bsd_dot_mb_id = self.bsd_dat_coc_id.bsd_dot_mb_id
        if self.bsd_loai_td == 'dong_sh':
            self.bsd_dsh_ht_ids = [(6, 0, self.bsd_dat_coc_id.bsd_dong_sh_ids.ids)]
        elif self.bsd_loai_td == 'khuyen_mai':
            self.bsd_km_ht_ids = [(6, 0, self.bsd_dat_coc_id.bsd_km_ids.ids)]

    state = fields.Selection([('nhap', 'Nháp'),
                              ('xac_nhan', 'Xác nhận'),
                              ('duyet', 'Duyệt'),
                              ('huy', 'Hủy')], string="Trạng thái", help="Trạng thái",
                             required=True, default='nhap', tracking=1)
    bsd_nguoi_duyet_id = fields.Many2one('res.users', string="Người duyệt", readonly=True)
    bsd_ngay_duyet = fields.Date(string="Ngày duyệt", readonly=True)
    bsd_nguoi_xn_id = fields.Many2one('res.users', string="Người xác nhận", readonly=True)
    bsd_ngay_xn = fields.Date(string="Ngày xác nhận", readonly=True)

    # KD Xác nhận phiếu chuyển người đại diện đặt cọc
    def action_xac_nhan(self):
        # Kiểm tra đặt cọc đã tạo hợp đồng chưa và đặt cọc còn hiệu lực không
        if self.bsd_dat_coc_id.state not in ['da_tc']:
            raise UserError("Đặt cọc đã hết hiệu lực.\nVui lòng kiểm tra lại thông tin.")
        if self.state == 'nhap':
            self.write({
                'state': 'xac_nhan',
                'bsd_ngay_xn': fields.Date.today(),
                'bsd_nguoi_xn_id': self.env.uid,
            })

    def action_duyet(self):
        # Kiểm tra đặt cọc đã tạo hợp đồng chưa và đặt cọc còn hiệu lực không
        if self.bsd_dat_coc_id.state not in ['da_tc']:
            raise UserError("Đặt cọc đã hết hiệu lực.\nVui lòng kiểm tra lại thông tin.")
        if self.state == 'xac_nhan':
            self.write({
                'state': 'duyet',
                'bsd_nguoi_duyet_id': self.env.uid,
                'bsd_ngay_duyet': fields.Date.today(),
            })
        # Thay đổi thông tin đồng sở hữu
        if self.bsd_loai_td == 'dong_sh':
            if len(self.bsd_dsh_moi_ids) != len(self.bsd_dsh_moi_ids.mapped('bsd_dong_sh_id')):
                raise UserError(_("Đồng sở hữu bị trùng dữ liệu. Vui lòng kiểm tra lại thông tin."))
            self.bsd_dat_coc_id.write({
                'bsd_dong_sh_ids': [(6, 0, self.bsd_dsh_moi_ids.ids)]
            })

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
            raise UserError(_('Dự án chưa có mã phiếu thay đổi thông tin đặt cọc.'))
        vals['bsd_ma'] = sequence.next_by_id()
        return super(BsdThayDoiThongTinDatCoc, self).create(vals)
