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
    _order = 'bsd_ngay desc'

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
                                    ('ck_tm', "Chiết khấu thương mại"),
                                    ('ck_db', "Chiết khấu đặt biệt")], string="Loại", default='dong_sh',
                                   required=True, readonly=True, states={'nhap': [('readonly', False)]})
    bsd_dsh_ht_ids = fields.Many2many('bsd.dong_so_huu', string="Đồng sở hữu ht", readonly=True)
    bsd_dsh_moi_ids = fields.One2many('bsd.dong_so_huu', 'bsd_td_tt_id', string="Đồng sở hữu mới", readonly=True,
                                      states={'xac_nhan': [('readonly', False)]})
    bsd_km_ht_ids = fields.Many2many('bsd.bao_gia_km', string="Khuyến mãi hiện tại", readonly=True)
    bsd_km_moi_ids = fields.One2many('bsd.bao_gia_km', 'bsd_td_tt_id', string="Khuyến mãi mới", readonly=True,
                                     states={'xac_nhan': [('readonly', False)]})
    bsd_cs_tt_ht_id = fields.Many2one('bsd.cs_tt', string="PTTT hiện tại", readonly=True)
    bsd_cs_tt_moi_id = fields.Many2one('bsd.cs_tt', string="PTTT mới", readonly=True,
                                       states={'xac_nhan': [('readonly', False)]})
    bsd_ps_ck_ht_ids = fields.Many2many('bsd.ps_ck', string="Chiết khấu hiện tại", readonly=True)
    bsd_ps_ck_moi_ids = fields.One2many('bsd.ps_ck', 'bsd_td_tt_id', string="Chiết khấu mới", readonly=True,
                                        states={'xac_nhan': [('readonly', False)]})
    bsd_ck_db_ht_ids = fields.Many2many('bsd.ck_db', string="CK đặt biệt hiện tại", readonly=True)
    bsd_ck_db_moi_ids = fields.One2many('bsd.ck_db', 'bsd_td_tt_id', string="CK đặt biệt mới", readonly=True,
                                        states={'xac_nhan': [('readonly', False)]})
    bsd_bg_ht_ids = fields.Many2many('bsd.ban_giao', string="ĐKBG hiện tại", help="Điều kiện bàn giao hiện tại", readonly=True)
    bsd_bg_moi_ids = fields.One2many('bsd.ban_giao', 'bsd_td_tt_id', string="Điều kiện bàn giao", readonly=True,
                                     states={'xac_nhan': [('readonly', False)]})
    bsd_ltt_ids = fields.Many2many('bsd.lich_thanh_toan', string="Lịch thanh toán", readonly=True)

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
        elif self.bsd_loai_td == 'pt_tt':
            self.bsd_cs_tt_ht_id = self.bsd_dat_coc_id.bsd_cs_tt_id
            self.bsd_ps_ck_ht_ids = [(6, 0, self.bsd_dat_coc_id.bsd_ps_ck_ids.filtered(lambda x: x.bsd_cs_tt_id).ids)]
            self.bsd_ltt_ids = [(6, 0, self.bsd_dat_coc_id.bsd_ltt_ids.ids)]
        elif self.bsd_loai_td == 'ck_tm':
            self.bsd_ps_ck_ht_ids = [(6, 0, self.bsd_dat_coc_id.bsd_ps_ck_ids.ids)]
            self.bsd_ltt_ids = [(6, 0, self.bsd_dat_coc_id.bsd_ltt_ids.ids)]
        elif self.bsd_loai_td == 'ck_db':
            self.bsd_ck_db_ht_ids = [(6, 0, self.bsd_dat_coc_id.bsd_ck_db_ids.ids)]
            self.bsd_ltt_ids = [(6, 0, self.bsd_dat_coc_id.bsd_ltt_ids.ids)]
        elif self.bsd_loai_td == 'dk_bg':
            self.bsd_bg_ht_ids = [(6, 0, self.bsd_dat_coc_id.bsd_bg_ids.ids)]
            self.bsd_ltt_ids = [(6, 0, self.bsd_dat_coc_id.bsd_ltt_ids.ids)]

    state = fields.Selection([('nhap', 'Nháp'),
                              ('xac_nhan', 'Xác nhận'),
                              ('duyet', 'Duyệt'),
                              ('huy', 'Hủy')], string="Trạng thái", help="Trạng thái",
                             required=True, default='nhap', tracking=1)
    bsd_nguoi_duyet_id = fields.Many2one('res.users', string="Người duyệt", readonly=True)
    bsd_ngay_duyet = fields.Date(string="Ngày duyệt", readonly=True)
    bsd_nguoi_xn_id = fields.Many2one('res.users', string="Người xác nhận", readonly=True)
    bsd_ngay_xn = fields.Date(string="Ngày xác nhận", readonly=True)

    @api.constrains('bsd_cs_tt_ht_id', 'bsd_cs_tt_moi_id')
    def _constraint_pt_tt(self):
        if self.bsd_loai_td == 'pt_tt':
            if self.bsd_cs_tt_moi_id == self.bsd_cs_tt_ht_id:
                raise UserError(_("Không thể chọn trùng với phương thức hiện tại. Vui lòng kiểm tra lại thông tin."))

    @api.onchange("bsd_cs_tt_moi_id")
    def _onchange_cs_tt(self):
        self.sudo().write({
            'bsd_ps_ck_moi_ids': [(5,)]
        })

    def action_chon_ck(self):
        action = self.env.ref('bsd_kinh_doanh.bsd_wizard_chon_ck_action').read()[0]
        return action

    def action_chon_ck_pttt(self):
        action = self.env.ref('bsd_kinh_doanh.bsd_wizard_chon_ck_pttt_action').read()[0]
        action['context'] = {'loai': 'ltt'}
        return action

    def action_chon_dkbg(self):
        action = self.env.ref('bsd_kinh_doanh.bsd_wizard_chon_dkbg_action').read()[0]
        return action

    def action_ck_db(self):
        action = self.env.ref('bsd_kinh_doanh.bsd_ck_db_td_tt_action_popup').read()[0]
        action['context'] = {'default_bsd_td_tt_id': self.id}
        return action

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
            raise UserError("Đặt cọc đã được ký hoặc đã hết hiệu lực.\nVui lòng kiểm tra lại thông tin.")
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
            message = ''
            # Các đồng sở hữu hết hiệu lực
            dsh_ht = self.bsd_dsh_ht_ids.mapped('bsd_dong_sh_id')
            if dsh_ht:
                message += "<li>Đồng sở hữu hết hiệu lực : {}</li>".format(
                    ','.join(dsh_ht.mapped('display_name')))
            # Các đồng sở hữu cập nhật mới
            dsh_moi = self.bsd_dsh_moi_ids.mapped('bsd_dong_sh_id')
            if dsh_moi:
                message += "<li>Đồng sở hữu mới: {}</li>".format(','.join(dsh_moi.mapped('display_name')))
            if message:
                self.bsd_dat_coc_id.message_post(body='<ul>' + message + '</ul>')
        # Thay đổi thông tin khuyến mãi
        elif self.bsd_loai_td == 'khuyen_mai':
            if len(self.bsd_km_moi_ids) != len(self.bsd_km_moi_ids.mapped('bsd_khuyen_mai_id')):
                raise UserError(_("Khuyến mãi bị trùng dữ liệu. Vui lòng kiểm tra lại thông tin."))
            self.bsd_dat_coc_id.write({
                'bsd_km_ids': [(6, 0, self.bsd_km_moi_ids.ids)]
            })
            message = ''
            # các khuyến mãi ngưng áp dụng cho đặt cọc
            km_ht = self.bsd_km_ht_ids.mapped('bsd_khuyen_mai_id')
            if km_ht:
                message += "<li>Ngưng áp dụng khuyến mãi : {}</li>".format(
                    ','.join(km_ht.mapped('bsd_ten_km')))
            # các khuyến mãi mới áp dụng cho đặt cọc
            km_moi = self.bsd_km_moi_ids.mapped('bsd_khuyen_mai_id')
            if km_moi:
                message += "<li>Áp dụng khuyến mãi: {}</li>".format(','.join(km_moi.mapped('bsd_ten_km')))
            if message:
                self.bsd_dat_coc_id.message_post(body='<ul>' + message + '</ul>')
        # Thay đổi thông tin phương thức thanh toán
        elif self.bsd_loai_td == 'pt_tt':
            if len(self.bsd_ps_ck_moi_ids) != len(self.bsd_ps_ck_moi_ids.mapped('bsd_chiet_khau_id')):
                raise UserError(_("Chiết khấu theo PTTT bị trùng dữ liệu. Vui lòng kiểm tra lại thông tin."))
            # Cập nhật phương thức thanh toán mới
            self.bsd_dat_coc_id.write({
                'bsd_cs_tt_id': self.bsd_cs_tt_moi_id.id
            })
            # bỏ liên kết chiết khấu theo pttt hiện tại
            for ck_pttt in self.bsd_ps_ck_ht_ids:
                self.bsd_dat_coc_id.write({
                    'bsd_ps_ck_ids': [(3, ck_pttt.id)]
                })
            # Ghi nhận chiết khấu theo phương thức thanh toán mới
            for ck_pttt_moi in self.bsd_ps_ck_moi_ids:
                self.bsd_dat_coc_id.write({
                    'bsd_ps_ck_ids': [(4, ck_pttt_moi.id)]
                })
            # Tính lại lịch thanh toán
            self.bsd_dat_coc_id.action_lich_tt()
            # ghi chú
            message = ''
            # Phương thức thanh toán hiện tại
            if self.bsd_cs_tt_ht_id:
                message += "<li>Ngưng áp dụng PTTT: {}</li>".format(
                    ','.join(self.bsd_cs_tt_ht_id.bsd_ten_cstt))
            # Chiết khấu theo phương thức thanh toán ngưng áp dụng
            if self.bsd_ps_ck_ht_ids:
                message += "<li>Ngưng áp dụng chiết khấu: {}</li>".format(
                    ','.join(self.self.bsd_ps_ck_ht_ids.mapped('bsd_chiet_khau_id').mapped('bsd_ten_ck')))
            # Phương thức thanh toán mới
            if self.bsd_cs_tt_moi_id:
                message += "<li>Áp dụng PTTT: {}</li>".format(','.join(self.bsd_cs_tt_moi_id.bsd_ten_cstt))
            if self.bsd_ps_ck_moi_ids:
                message += "<li>Áp dụng chiết khấu: {}</li>".format(
                    ','.join(self.self.bsd_ps_ck_moi_ids.mapped('bsd_chiet_khau_id').mapped('bsd_ten_ck')))
            if message:
                self.bsd_dat_coc_id.message_post(body='<ul>' + message + '</ul>')
        # Thay đổi chiết khấu thương mại
        elif self.bsd_loai_td == 'ck_tm':
            if len(self.bsd_ps_ck_moi_ids) != len(self.bsd_ps_ck_moi_ids.mapped('bsd_chiet_khau_id')):
                raise UserError(_("Chiết khấu bị trùng dữ liệu. Vui lòng kiểm tra lại thông tin."))
            # bỏ liên kết chiết khấu theo pttt hiện tại
            for ck_pttt in self.bsd_ps_ck_ht_ids:
                self.bsd_dat_coc_id.write({
                    'bsd_ps_ck_ids': [(3, ck_pttt.id)]
                })
            # Ghi nhận chiết khấu theo phương thức thanh toán mới
            for ck_pttt_moi in self.bsd_ps_ck_moi_ids:
                self.bsd_dat_coc_id.write({
                    'bsd_ps_ck_ids': [(4, ck_pttt_moi.id)]
                })
            # Tính lại lịch thanh toán
            self.bsd_dat_coc_id.action_lich_tt()
            # ghi chú
            message = ''
            # Chiết khấu ngưng áp dụng
            if self.bsd_ps_ck_ht_ids:
                message += "<li>Ngưng áp dụng chiết khấu: {}</li>".format(
                    ','.join(self.bsd_ps_ck_ht_ids.mapped('bsd_chiet_khau_id').mapped('bsd_ten_ck')))
            if self.bsd_ps_ck_moi_ids:
                message += "<li>Áp dụng chiết khấu: {}</li>".format(
                    ','.join(self.bsd_ps_ck_moi_ids.mapped('bsd_chiet_khau_id').mapped('bsd_ten_ck')))
            if message:
                self.bsd_dat_coc_id.message_post(body='<ul>' + message + '</ul>')
        # Thay đổi chiết khấu đặc biệt
        elif self.bsd_loai_td == 'ck_db':
            # bỏ liên kết chiết khấu đặt biệt hiện tại
            for ck_db_ht in self.bsd_ck_db_ht_ids:
                self.bsd_dat_coc_id.write({
                    'bsd_ck_db_ids': [(3, ck_db_ht.id)]
                })
            # Ghi nhận chiết khấu đặt biệt:
            for ck_db_moi in self.bsd_ck_db_moi_ids:
                self.bsd_dat_coc_id.write({
                    'bsd_ck_db_ids': [(4, ck_db_moi.id)]
                })
            # Tính lại lịch thanh toán
            self.bsd_dat_coc_id.action_lich_tt()
            # ghi chú
            message = ''
            # Chiết khấu đặt biệttoán ngưng áp dụng
            if self.bsd_ck_db_ht_ids:
                message += "<li>Ngưng áp dụng chiết khấu đặc biệt: {}</li>".format(
                    ','.join(self.bsd_ck_db_ht_ids.mapped('bsd_ten_ck_db')))
            if self.bsd_ck_db_moi_ids:
                message += "<li>Áp dụng chiết khấu đặt biệt: {}</li>".format(
                    ','.join(self.bsd_ck_db_moi_ids.mapped('bsd_ten_ck_db')))
            if message:
                self.bsd_dat_coc_id.message_post(body='<ul>' + message + '</ul>')
        # Thay đổi điều kiện bàn giao
        elif self.bsd_loai_td == 'dk_bg':
            # bỏ liên kết điều kiện bàn giao
            for bg_ht in self.bsd_bg_ht_ids:
                self.bsd_dat_coc_id.write({
                    'bsd_bg_ids': [(3, bg_ht.id)]
                })
            # Ghi nhận điều kiện bàn giao mới
            for bg_moi in self.bsd_bg_moi_ids:
                self.bsd_dat_coc_id.write({
                    'bsd_bg_ids': [(4, bg_moi.id)]
                })
            # Tính lại lịch thanh toán
            self.bsd_dat_coc_id.action_lich_tt()
            # ghi chú
            message = ''
            # Điều kiện bàn giao ngưng áp dụng
            if self.bsd_bg_ht_ids:
                message += "<li>Ngưng áp dụng ĐKBG: {}</li>".format(
                    ','.join(self.bsd_bg_ht_ids.mapped('bsd_dk_bg_id').mapped('bsd_ten_dkbg')))
            if self.bsd_bg_moi_ids:
                message += "<li>Áp dụng ĐKBG: {}</li>".format(
                    ','.join(self.bsd_bg_moi_ids.mapped('bsd_dk_bg_id').mapped('bsd_ten_dkbg')))
            if message:
                self.bsd_dat_coc_id.message_post(body='<ul>' + message + '</ul>')

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
