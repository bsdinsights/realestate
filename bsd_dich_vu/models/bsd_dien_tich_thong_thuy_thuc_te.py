# -*- coding:utf-8 -*-

from odoo import models, fields, api
from odoo.tools.float_utils import float_round
from odoo.exceptions import UserError


class BsdDTTTTT(models.Model):
    _name = 'bsd.dt_tt'
    _description = "Diện tích thông thủy thực tế"
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _rec_name = "bsd_so_ct"

    bsd_so_ct = fields.Char(string="Số chứng từ", help="Số chứng từ", required=True,
                                    readonly=True,
                                    states={'nhap': [('readonly', False)]})
    _sql_constraints = [
        ('bsd_so_ct_unique', 'unique (bsd_so_ct)',
         'Số chứng từ đã tồn tại !'),
    ]
    bsd_ngay_ct = fields.Datetime(string="Ngày cập nhật", help="Ngày cập nhật", required=True,
                                  default=fields.Datetime.now(),
                                  readonly=True,
                                  states={'nhap': [('readonly', False)]})
    bsd_so_lan = fields.Integer(string="Lần cập nhật", help="Lần cập nhật",
                                readonly=True,
                                states={'nhap': [('readonly', False)]})
    bsd_du_an_id = fields.Many2one('bsd.du_an', string="Dự án", help="Tên dự án", required=True,
                                   readonly=True,
                                   states={'nhap': [('readonly', False)]})
    bsd_unit_id = fields.Many2one('product.product', string="Căn hộ", help="Tên căn hộ", required=True,
                                  readonly=True,
                                  states={'nhap': [('readonly', False)]})
    bsd_dt_tt_tt = fields.Float(string="Diện tích thực tế", help="Diện tích thông thủy thực tế", required=True,
                                readonly=True,
                                states={'nhap': [('readonly', False)]})
    bsd_dt_tt_tk = fields.Float(string="Diện tích thiết kế",
                                help="Diện tích thông thủy thiết kế", related="bsd_unit_id.bsd_dt_sd")
    bsd_dt_cl_tt = fields.Float(string="% Chênh lệch thực tế", help="% Chênh lệch thực tế", readonly=True,
                                compute='_compute_dt_cl_tt', store=True)
    bsd_dt_cl = fields.Float(string="% Chênh lệch cho phép", help="% Chênh lệch cho phép",
                             related="bsd_unit_id.bsd_dt_cl")
    bsd_dien_giai = fields.Char(string="Diễn giải", help="Diễn giải",
                                readonly=True,
                                states={'nhap': [('readonly', False)]})
    bsd_phu_luc = fields.Boolean(string="Phụ lục", help="Có làm phụ lục hay không", compute='_compute_pl', store=True)
    bsd_loai_pl = fields.Selection([('td_tt', 'Thay đổi thông tin'), ('td_dt', 'Thay đổi diện tích')],
                                   string="Loại phụ lục", compute='_compute_loai_pl', store=True)
    state = fields.Selection([('nhap', 'Nháp'), ('xac_nhan', 'Xác nhận'),
                              ('duyet', 'Duyệt'), ('huy', 'Hủy')],
                             string="Trạng thái", help="Trạng thái", required=True, default="nhap", tracking=1)

    @api.depends('bsd_dt_tt_tt', 'bsd_dt_tt_tk')
    def _compute_dt_cl_tt(self):
        for each in self:
            if each.bsd_dt_tt_tk != 0:
                each.bsd_dt_cl_tt = 100 - (float_round((each.bsd_dt_tt_tt / each.bsd_dt_tt_tk) * 100, precision_digits=2))

    # DV.18.01 - Xác nhận cập nhật diện tích thực tế
    def action_xac_nhan(self):
        self.write({
            'state': 'xac_nhan'
        })

    # DV.18.02 - Duyệt thông tin diện tích thực tế
    def action_duyet(self):
        self.write({
            'state': 'duyet',
        })

    # DV.18.03 - Hủy thông tin diện tích thực tế
    def action_huy(self):
        pl_tti = self.env['bsd.pl_tti'].search([('bsd_dt_tt_id', '=', self.id),
                                                ('state', '!=', 'huy')])
        if pl_tti:
            raise UserError("Đã phát sinh Phụ lục hợp đồng thay đổi thông tin\n "
                            "Bạn không thể Hủy, vui lòng kiểm tra lại")
        else:
            self.write({
                'state': 'huy',
            })

    @api.depends('bsd_dt_cl_tt')
    def _compute_pl(self):
        for each in self:
            each.bsd_phu_luc = True if each.bsd_dt_cl_tt != 0 else False

    @api.depends('bsd_dt_cl_tt', 'bsd_dt_cl')
    def _compute_loai_pl(self):
        for each in self:
            if each.bsd_dt_cl_tt == 0:
                each.bsd_loai_pl = None
            else:
                if abs(each.bsd_dt_cl_tt) > each.bsd_dt_cl:
                    each.bsd_loai_pl = 'td_dt'
                elif abs(each.bsd_dt_cl_tt) <= each.bsd_dt_cl:
                    each.bsd_loai_pl = 'td_tt'
