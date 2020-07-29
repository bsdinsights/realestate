# -*- coding:utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError
import logging

_logger = logging.getLogger(__name__)


class BsdThongBaoBanGiao(models.Model):
    _name = 'bsd.tb_bg'
    _description = "Thông báo bàn giao"
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _rec_name = 'bsd_ma_tb'

    bsd_ma_tb = fields.Char(string="Mã", help="Mã thông báo bàn giao", required=True, readonly=True,
                            copy=False, default='/')
    _sql_constraints = [
        ('bsd_ma_tb_unique', 'unique (bsd_ma_tb)',
         'Mã thông báo đã tồn tại !')
    ]
    bsd_ngay_tao_tb = fields.Datetime(string="Ngày", help="Ngày tạo thông báo bàn giao",
                                      required=True, default=lambda self: fields.Datetime.now(),
                                      readonly=True,
                                      states={'nhap': [('readonly', False)]})
    bsd_doi_tuong = fields.Char(string="Đối tượng", help="Đối tượng được tạo thông báo", required=True,
                                readonly=True,
                                states={'nhap': [('readonly', False)]})
    bsd_tao_td = fields.Boolean(string="Được tạo tự động", help="Đánh dấu thông báo được tạo tự động từ hệ thông",
                                readonly=True)
    bsd_cn_dkbg_unit_id = fields.Many2one('bsd.cn_dkbg_unit', string="Cập nhật DKBG chi tiết",
                                          help="Mã cập nhật DKBG chi tiết",
                                          readonly=True, required=True,
                                          states={'nhap': [('readonly', False)]})
    bsd_ngay_bg = fields.Date(string="Ngày bàn giao", help="Ngày bàn giao",
                              readonly=True,
                              states={'nhap': [('readonly', False)]})
    bsd_ngay_tb = fields.Date(string="Ngày thông báo", help="Ngày thông báo bàn giao",
                              readonly=True,
                              states={'nhap': [('readonly', False)]})
    bsd_ngay_ut = fields.Date(string="Ngày ước tính", help="Ngày ước tính",
                              readonly=True,
                              states={'nhap': [('readonly', False)]})
    bsd_ngay_in = fields.Datetime(string="Ngày in", help="Ngày in thông báo bàn giao", readonly=True)
    bsd_nguoi_ht_id = fields.Many2one("res.users", help="Người thực hiện thông báo thành công",
                                      string="Người hoàn thành",
                                      readonly=True)
    bsd_ngay_gui = fields.Datetime(string="Ngày gửi", help="Ngày gửi bàn giao", readonly=True)
    bsd_ngay_ht = fields.Datetime(string="Ngày hoàn thành", help="Ngày xác nhận thông báo thành công", readonly=True)
    bsd_du_an_id = fields.Many2one('bsd.du_an', string="Dự án", help="Dự án", required=True,
                                   readonly=True,
                                   states={'nhap': [('readonly', False)]})
    bsd_unit_id = fields.Many2one('product.product', string="Sản phẩm", help="Sản phẩm", required=True,
                                  readonly=True,
                                  states={'nhap': [('readonly', False)]})
    bsd_hd_ban_id = fields.Many2one('bsd.hd_ban', string="Hợp đồng", help="Hợp đồng", required=True,
                                    readonly=True,
                                    states={'nhap': [('readonly', False)]})
    bsd_dot_tt_id = fields.Many2one('bsd.lich_thanh_toan', string="Đợt thanh toán",
                                    help="Đợt thanh toán là Đợt dự kiến bàn giao", compute="_compute_dot_tt")
    bsd_ngay_hh_tt = fields.Date(string="Hạn thanh toán", help="Hạn thanh toán của đợt dự kiến bàn giao",
                                 compute="_compute_dot_tt")

    @api.onchange('bsd_cn_dkbg_unit_id')
    def _onchange_dkbg_unit(self):
        self.bsd_ngay_bg = self.bsd_cn_dkbg_unit_id.bsd_ngay_dkbg_moi
        self.bsd_ngay_tb = fields.Datetime.now()
        self.bsd_ngay_ut = self.bsd_cn_dkbg_unit_id.bsd_cn_dkbg_id.bsd_ngay_ut
        self.bsd_du_an_id = self.bsd_cn_dkbg_unit_id.bsd_du_an_id
        self.bsd_hd_ban_id = self.bsd_cn_dkbg_unit_id.bsd_hd_ban_id
        self.bsd_unit_id = self.bsd_cn_dkbg_unit_id.bsd_unit_id

    bsd_ngay_dkbg = fields.Date(related="bsd_hd_ban_id.bsd_ngay_dkbg")
    bsd_khach_hang_id = fields.Many2one('res.partner', string="Khách hàng", help="Khách hàng", required=True,
                                        readonly=True,
                                        states={'nhap': [('readonly', False)]})
    bsd_tien_ng = fields.Monetary(string="Nợ gốc",
                                  help="Tổng số tiền đợt thanh toán mà khách hàng chưa thanh toán và "
                                       "không bao gồm đợt thanh toán cuối")
    bsd_tien_pbt = fields.Monetary(string="Phí bảo trì", help="Phí bảo trì cần phải thu của khách hàng")
    bsd_tien_pql = fields.Monetary(string="Phí quản lý", help="Phí quản lý cần phải thu của khách hàng")
    bsd_thang_pql = fields.Integer(string="Số tháng đóng PQL", related='bsd_unit_id.bsd_thang_pql',
                                   help="Số tháng đóng phí quản lý được quy định trên sản phẩm")
    bsd_don_gia_pql = fields.Monetary(string="Đơn giá PQL", related='bsd_unit_id.bsd_don_gia_pql',
                                      help="Đơn giá phí quản lý được quy định trên sản phẩm")
    company_id = fields.Many2one('res.company', string='Công ty', default=lambda self: self.env.company)
    currency_id = fields.Many2one(related="company_id.currency_id", string="Tiền tệ", readonly=True)
    state = fields.Selection([('nhap', 'Nháp'),
                              ('xac_nhan', 'Xác nhận'),
                              ('hoan_thanh', 'Hoàn thành'),
                              ('huy', 'Hủy')],
                             string="Trạng thái", default="nhap", required=True, readonly=True, tracking=1)
    bsd_so_bg_sp = fields.Integer(string="# Bàn giao sp", compute="_compute_bg_sp")

    @api.onchange('bsd_hd_ban_id')
    def _onchange_hd_ban(self):
        self.bsd_khach_hang_id = self.bsd_hd_ban_id.bsd_khach_hang_id
        self.bsd_tien_pbt = self.bsd_hd_ban_id.bsd_tien_pbt
        self.bsd_tien_pql = self.bsd_hd_ban_id.bsd_tien_pql
        dot_cuoi = self.bsd_hd_ban_id.bsd_ltt_ids.filtered(lambda x: x.bsd_cs_tt_ct_id.bsd_dot_cuoi)
        self.bsd_tien_ng = self.bsd_hd_ban_id.bsd_tong_gia - self.bsd_hd_ban_id.bsd_tien_pbt - self.bsd_hd_ban_id.bsd_tien_tt_hd - dot_cuoi.bsd_tien_dot_tt

    @api.depends('bsd_hd_ban_id')
    def _compute_dot_tt(self):
        for each in self:
            dot_dkbg = each.bsd_hd_ban_id.bsd_ltt_ids.filtered(lambda x: x.bsd_ma_dtt == 'DKBG')
            each.bsd_dot_tt_id = dot_dkbg.id
            each.bsd_ngay_hh_tt = dot_dkbg.bsd_ngay_hh_tt

    def _compute_bg_sp(self):
        for each in self:
            # ban_giao = self.env['bsd.bg_sp'].search([('bsd_tb_nt_id', '=', self.id)])
            each.bsd_so_bg_sp = 1

    # def action_view_ban_giao(self):
    #     action = self.env.ref('bsd_kinh_doanh.bsd_ban_giao_action').read()[0]
    #
    #     ban_giao = self.env['bsd.ban_giao'].search([('bsd_tb_nt_id', '=', self.id)])
    #     if len(ban_giao) > 1:
    #         action['domain'] = [('id', 'in', ban_giao.ids)]
    #     elif ban_giao:
    #         form_view = [(self.env.ref('bsd_kinh_doanh.bsd_ban_giao_form').id, 'form')]
    #         if 'views' in action:
    #             action['views'] = form_view + [(state, view) for state, view in action['views'] if view != 'form']
    #         else:
    #             action['views'] = form_view
    #         action['res_id'] = ban_giao.id
    #     # Prepare the context.
    #     context = {
    #         'default_bsd_tb_nt_id': self.id,
    #     }
    #     action['context'] = context
    #     return action

    # DV.16.01 Xác nhận thông báo bàn giao
    def action_xac_nhan(self):
        if self.state == 'nhap':
            self.write({
                'state': 'xac_nhan'
            })

    # DV.16.02 In thông báo bàn giao
    def action_in_tb(self):
        return self.env.ref('bsd_dich_vu.bsd_tb_bg_report_action').read()[0]

    # DV.16.03 Cập nhật ngày gửi
    def action_gui_tb(self):
        action = self.env.ref('bsd_dich_vu.bsd_wizard_tb_bg_action').read()[0]
        _logger.debug(action)
        return action

    # DV.16.04 Hoàn thành thông báo bàn giao
    def action_hoan_thanh(self):
        if self.state == 'xac_nhan':
            self.write({
                'state': 'hoan_thanh',
                'bsd_ngay_ht': fields.Datetime.now(),
                'bsd_nguoi_ht_id': self.env.uid,
            })

    # DV.16.05 Hủy thông báo bàn giao
    def action_huy(self):
        if self.state == 'nhap':
            self.write({
                'state': 'huy'
            })

    # DV.16.06 Kiểm tra điều kiện của cập nhật DKBG chi tiết
    @api.constrains('bsd_hd_ban_id')
    def _constrains_hd_ban(self):
        if self.bsd_hd_ban_id.state == 'thanh_ly':
            raise UserError(_('Hợp đồng đã bị thanh lý. Vui lòng kiểm tra lại!'))

    @api.model
    def create(self, vals):
        sequence = False
        if 'bsd_du_an_id' in vals:
            du_an = self.env['bsd.du_an'].browse(vals['bsd_du_an_id'])
            sequence = du_an.get_ma_bo_cn(loai_cn=self._name)
        if not sequence:
            raise UserError(_('Dự án chưa có mã thông báo bàn giao'))
        vals['bsd_ma_tb'] = sequence.next_by_id()
        return super(BsdThongBaoBanGiao, self).create(vals)