# -*- coding:utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError
from odoo.tools.float_utils import float_round
import logging

_logger = logging.getLogger(__name__)


class BsdThongBaoBanGiao(models.Model):
    _name = 'bsd.tb_bg'
    _description = "Thông báo bàn giao"
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _rec_name = 'bsd_ma_tb'
    _order = 'bsd_ngay_tao_tb desc'

    bsd_ma_tb = fields.Char(string="Mã", help="Mã thông báo bàn giao", required=True, readonly=True,
                            copy=False, default='/')
    _sql_constraints = [
        ('bsd_ma_tb_unique', 'unique (bsd_ma_tb)',
         'Mã thông báo đã tồn tại !')
    ]
    bsd_ngay_tao_tb = fields.Date(string="Ngày", help="Ngày tạo thông báo bàn giao",
                                  required=True, default=lambda self: fields.Date.today(),
                                  readonly=True,
                                  states={'nhap': [('readonly', False)]})
    bsd_doi_tuong = fields.Char(string="Đối tượng", help="Đối tượng được tạo thông báo", required=True,
                                readonly=True,
                                states={'nhap': [('readonly', False)]})
    bsd_tao_td = fields.Boolean(string="Được tạo tự động", help="Đánh dấu thông báo được tạo tự động từ hệ thông",
                                readonly=True)
    bsd_cn_dkbg_unit_id = fields.Many2one('bsd.cn_dkbg_unit', string="CN.DKBG chi tiết",
                                          help="Mã cập nhật DKBG chi tiết",
                                          readonly=True)
    bsd_ngay_bg = fields.Date(string="Ngày bàn giao", help="Ngày bàn giao",
                              readonly=True, required=True,
                              states={'nhap': [('readonly', False)]})
    bsd_ngay_ut = fields.Date(string="Ngày ước tính", help="Ngày ước tính",
                              readonly=True, required=True,
                              states={'nhap': [('readonly', False)]})
    bsd_ngay_in = fields.Date(string="Ngày in", help="Ngày in thông báo bàn giao", readonly=True)
    bsd_nguoi_ht_id = fields.Many2one("res.users", help="Người thực hiện thông báo thành công",
                                      string="Người hoàn thành",
                                      readonly=True)
    bsd_ngay_gui = fields.Date(string="Ngày gửi", help="Ngày gửi bàn giao", readonly=True)
    bsd_ngay_ht = fields.Date(string="Ngày hoàn thành", help="Ngày xác nhận thông báo thành công", readonly=True)
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
                                    help="Đợt thanh toán là Đợt dự kiến bàn giao",
                                    readonly=True,
                                    states={'nhap': [('readonly', False)]})
    bsd_ngay_hh_tt = fields.Date(string="Hạn thanh toán", help="Hạn thanh toán của đợt dự kiến bàn giao",
                                 readonly=True,
                                 states={'nhap': [('readonly', False)]})
    bsd_ngay_dkbg = fields.Date(string="Ngày DKBG", help="Ngày dự kiến bàn giao",
                                readonly=True,
                                states={'nhap': [('readonly', False)]})
    bsd_khach_hang_id = fields.Many2one('res.partner', string="Khách hàng", help="Khách hàng", required=True,
                                        readonly=True,
                                        states={'nhap': [('readonly', False)]})
    bsd_tien_ng = fields.Monetary(string="Nợ gốc",
                                  help="Tổng số tiền đợt thanh toán mà khách hàng chưa thanh toán và "
                                       "không bao gồm đợt thanh toán cuối",
                                  readonly=True,
                                  states={'nhap': [('readonly', False)]})
    bsd_tien_pbt = fields.Monetary(string="Phí bảo trì", help="Phí bảo trì cần phải thu của khách hàng",
                                   readonly=True,
                                   states={'nhap': [('readonly', False)]})
    bsd_tien_pql = fields.Monetary(string="Phí quản lý", help="Phí quản lý cần phải thu của khách hàng",
                                   readonly=True,
                                   states={'nhap': [('readonly', False)]})
    bsd_thang_pql = fields.Integer(string="Số tháng đóng PQL",
                                   help="Số tháng đóng phí quản lý được quy định trên sản phẩm",
                                   readonly=True,
                                   states={'nhap': [('readonly', False)]})
    bsd_don_gia_pql = fields.Monetary(string="Đơn giá PQL",
                                      help="Đơn giá phí quản lý được quy định trên sản phẩm",
                                      readonly=True,
                                      states={'nhap': [('readonly', False)]})
    bsd_tien_lp = fields.Monetary(string="Tiền phạt chậm TT", help="Tiền phạt chậm thanh toán của hợp đồng")
    company_id = fields.Many2one('res.company', string='Công ty', default=lambda self: self.env.company)
    currency_id = fields.Many2one(related="company_id.currency_id", string="Tiền tệ", readonly=True)
    state = fields.Selection([('nhap', 'Nháp'),
                              ('xac_nhan', 'Xác nhận'),
                              ('hoan_thanh', 'Hoàn thành'),
                              ('huy', 'Hủy')],
                             string="Trạng thái", default="nhap", required=True, readonly=True, tracking=1)
    bsd_tien_lp_ut = fields.Monetary(string="Tiền phạt ước tính", help="Tiền phạt chậm thanh toán của hợp đồng",
                                     readonly=True,
                                     states={'nhap': [('readonly', False)]})
    bsd_so_ngay_tre = fields.Integer(string="Số ngày trễ", help="Số ngày trễ được tính từ ngày ước tính",
                                     readonly=True,
                                     states={'nhap': [('readonly', False)]})
    bsd_tong_tien = fields.Monetary(string="Tổng tiền", help="Tổng tiền phải thanh toán bao gồm ước tính lãi phạt",
                                    compute='_compute_tong_tien')
    bsd_so_tb = fields.Integer(string="Số lần TB", help="Số lần hoàn thành thông báo bàn giao", readonly=True)
    meeting_count = fields.Integer('# Meetings', compute='_compute_meeting_count')

    def _compute_meeting_count(self):
        meeting_data = self.env['calendar.event'].read_group([('bsd_tb_bg_id', 'in', self.ids)], ['bsd_tb_bg_id'], ['bsd_tb_bg_id'])
        mapped_data = {m['bsd_tb_bg_id'][0]: m['bsd_tb_bg_id_count'] for m in meeting_data}
        for lead in self:
            lead.meeting_count = mapped_data.get(lead.id, 0)

    @api.depends('bsd_tien_ng', 'bsd_tien_pbt', 'bsd_tien_pql', 'bsd_tien_lp', 'bsd_tien_lp_ut')
    def _compute_tong_tien(self):
        for each in self:
            each.bsd_tong_tien = each.bsd_tien_ng + each.bsd_tien_pbt + \
                                 each.bsd_tien_pql + each.bsd_tien_lp + each.bsd_tien_lp_ut

    bsd_so_bg = fields.Integer(string="# Bàn giao", compute="_compute_bg")

    def _compute_bg(self):
        for each in self:
            bg_sp = self.env['bsd.bg_sp'].search([('bsd_tb_bg_id', '=', self.id)])
            each.bsd_so_bg = len(bg_sp)

    def action_view_ban_giao(self):
        action = self.env.ref('bsd_dich_vu.bsd_bg_sp_action').read()[0]

        bg_sp = self.env['bsd.bg_sp'].search([('bsd_tb_bg_id', '=', self.id)])
        if len(bg_sp) > 1:
            action['domain'] = [('id', 'in', bg_sp.ids)]
        elif bg_sp:
            form_view = [(self.env.ref('bsd_dich_vu.bsd_bg_sp_form').id, 'form')]
            if 'views' in action:
                action['views'] = form_view + [(state, view) for state, view in action['views'] if view != 'form']
            else:
                action['views'] = form_view
            action['res_id'] = bg_sp.id
        # Prepare the context.
        context = {
            'default_bsd_tb_bg_id': self.id,
        }
        action['context'] = context
        return action

    @api.onchange('bsd_hd_ban_id')
    def _onchange_hd_ban(self):
        self.bsd_khach_hang_id = self.bsd_hd_ban_id.bsd_khach_hang_id
        self.bsd_tien_pbt = self.bsd_hd_ban_id.bsd_tien_pbt
        self.bsd_tien_pql = self.bsd_hd_ban_id.bsd_tien_pql
        dot_cuoi = self.bsd_hd_ban_id.bsd_ltt_ids.filtered(lambda x: x.bsd_cs_tt_ct_id.bsd_dot_cuoi)
        self.bsd_tien_ng = self.bsd_hd_ban_id.bsd_tong_gia - self.bsd_hd_ban_id.bsd_tien_pbt - self.bsd_hd_ban_id.bsd_tien_tt_hd - dot_cuoi.bsd_tien_dot_tt

    # Ước tính tiền phạt chậm thanh toán
    def action_uoc_tinh_tien_phat(self):
        # Load các đợt chưa thanh toán của hợp đồng
        dot_tt_ids = self.bsd_hd_ban_id.bsd_ltt_ids\
            .filtered(lambda d: d.bsd_thanh_toan != 'da_tt' and d.bsd_ngay_hh_tt)\
            .sorted('bsd_stt')
        cs_tt = self.bsd_hd_ban_id.bsd_cs_tt_id
        tong_so_ngay_phat = 0
        tong_tien_phat = 0
        for dot_tt in dot_tt_ids:
            # Kiểm tra ngày làm mốc tính lãi phạt
            han_tinh_phat = dot_tt.bsd_ngay_hh_tt
            if dot_tt.bsd_tinh_phat == 'nah':
                han_tinh_phat = dot_tt.bsd_ngay_ah
            # Số ngày tính lãi phạt
            so_ngay_nam = cs_tt.bsd_lai_phat_tt_id.bsd_so_ngay_nam
            if self.bsd_ngay_ut > han_tinh_phat:
                # Số ngày tính phạt
                so_ngay_tp = (self.bsd_ngay_ut - han_tinh_phat).days
                # Tính lãi phạt
                tien_phat = float_round(dot_tt.bsd_tien_phai_tt * (dot_tt.bsd_lai_phat/100 / so_ngay_nam) * so_ngay_tp, 0)
                # Kiểm tra lãi phạt đã vượt lãi phạt tối đa của đợt chưa
                tong_tien_phat = dot_tt.bsd_tien_phat + tien_phat
                if dot_tt.bsd_tien_td == 0 and dot_tt.bsd_tl_td != 0:
                    tien_phat_toi_da = dot_tt.bsd_tien_dot_tt * dot_tt.bsd_tl_td / 100
                    if tong_tien_phat > tien_phat_toi_da:
                        tien_phat = tien_phat_toi_da - dot_tt.bsd_tien_phat
                elif dot_tt.bsd_tien_td != 0 and dot_tt.bsd_tl_td == 0:
                    tien_phat_toi_da = dot_tt.bsd_tien_td
                    if tong_tien_phat > tien_phat_toi_da:
                        tien_phat = tien_phat_toi_da - dot_tt.bsd_tien_phat
                elif dot_tt.bsd_tien_td != 0 and dot_tt.bsd_tl_td != 0:
                    tien_phat_toi_da_1 = dot_tt.bsd_tien_dot_tt * dot_tt.bsd_tl_td / 100
                    tien_phat_toi_da_2 = dot_tt.bsd_tien_td
                    tien_phat_toi_da = tien_phat_toi_da_1 if tien_phat_toi_da_1 < tien_phat_toi_da_2 else tien_phat_toi_da_2
                    if tong_tien_phat > tien_phat_toi_da:
                        tien_phat = tien_phat_toi_da - dot_tt.bsd_tien_phat
            else:
                so_ngay_tp = 0
                tien_phat = 0
            tong_tien_phat += tien_phat
            tong_so_ngay_phat += so_ngay_tp
        self.write({
            'bsd_so_ngay_tre': tong_so_ngay_phat,
            'bsd_tien_lp_ut': tong_tien_phat,
        })

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
        return action

    # DV.16.04 Hoàn thành thông báo bàn giao
    def action_hoan_thanh(self):
        if self.state == 'xac_nhan':
            self.write({
                'state': 'hoan_thanh',
                'bsd_ngay_ht': fields.Date.today(),
                'bsd_nguoi_ht_id': self.env.uid,
            })

    # DV.16.05 Hủy thông báo bàn giao
    def action_huy(self):
        if self.state in ['nhap', 'xac_nhan']:
            self.write({
                'state': 'huy'
            })

    # Tạo bàn giao sản phẩm
    def action_tao_bg(self):
        self.env['bsd.bg_sp'].create({
            'bsd_ten_bg': 'Bàn giao sản phẩm ' + self.bsd_unit_id.bsd_ma_unit,
            'bsd_tb_bg_id': self.id,
            'bsd_du_an_id': self.bsd_du_an_id.id,
            'bsd_hd_ban_id': self.bsd_hd_ban_id.id,
            'bsd_khach_hang_id': self.bsd_khach_hang_id.id,
            'bsd_unit_id': self.bsd_unit_id.id,
            'bsd_duyet_bgdb': self.bsd_hd_ban_id.bsd_duyet_bgdb,
            'bsd_tien_tt_hd': self.bsd_hd_ban_id.bsd_tien_tt_hd,
            'bsd_tl_tt_hd': self.bsd_hd_ban_id.bsd_tl_tt_hd,
            'bsd_dt_tt': self.bsd_hd_ban_id.bsd_unit_id.bsd_dt_tt,
            'bsd_ngay_dkbg': self.bsd_hd_ban_id.bsd_ngay_dkbg,
        })

    # DV.16.06 Kiểm tra điều kiện của cập nhật DKBG chi tiết
    @api.constrains('bsd_hd_ban_id')
    def _constrains_hd_ban(self):
        if self.bsd_hd_ban_id.state == 'thanh_ly':
            raise UserError(_('Hợp đồng đã bị thanh lý.\nVui lòng kiểm tra lại!'))

    # Hẹn ngày gặp khách hàng
    def action_schedule_meeting(self):
        self.ensure_one()
        action = self.env.ref('calendar.action_calendar_event').read()[0]
        partner_ids = self.env.user.partner_id.ids
        if self.bsd_khach_hang_id:
            partner_ids.append(self.bsd_khach_hang_id.id)
        action['context'] = {
            'default_bsd_tb_bg_id': self.id,
            'default_partner_id': self.bsd_khach_hang_id.id,
            'default_partner_ids': partner_ids,
            'default_name': self.bsd_doi_tuong,
        }
        return action

    def log_meeting(self, meeting_subject, meeting_date, duration):
        if not duration:
            duration = _('unknown')
        else:
            duration = str(duration)
        meet_date = fields.Datetime.from_string(meeting_date)
        meeting_usertime = fields.Datetime.to_string(fields.Datetime.context_timestamp(self, meet_date))
        html_time = "<time datetime='%s+00:00'>%s</time>" % (meeting_date, meeting_usertime)
        message = _("Meeting scheduled at '%s'<br> Subject: %s <br> Duration: %s hours") % (html_time, meeting_subject, duration)
        return self.message_post(body=message)

    @api.model
    def create(self, vals):
        sequence = False
        if 'bsd_du_an_id' in vals:
            du_an = self.env['bsd.du_an'].browse(vals['bsd_du_an_id'])
            sequence = du_an.get_ma_bo_cn(loai_cn=self._name)
        if not sequence:
            raise UserError(_('Dự án chưa có mã thông báo bàn giao.'))
        vals['bsd_ma_tb'] = sequence.next_by_id()
        return super(BsdThongBaoBanGiao, self).create(vals)


class CalendarEvent(models.Model):
    _inherit = 'calendar.event'

    @api.model
    def default_get(self, fields):
        if self.env.context.get('default_bsd_tb_bg_id'):
            self = self.with_context(
                default_res_model_id=self.env.ref('bsd_dich_vu.model_bsd_tb_bg').id,
                default_res_id=self.env.context['default_bsd_tb_bg_id']
            )
        if self.env.context.get('default_bsd_tb_nt_id'):
            self = self.with_context(
                default_res_model_id=self.env.ref('bsd_dich_vu.model_bsd_tb_nt').id,
                default_res_id=self.env.context['default_bsd_tb_nt_id']
            )
        defaults = super(CalendarEvent, self).default_get(fields)

        # sync res_model / res_id to thông báo bàn giao id
        if 'bsd_tb_bg_id' not in defaults and defaults.get('res_id') and (defaults.get('res_model') or defaults.get('res_model_id')):
            if (defaults.get('res_model') and defaults['res_model'] == 'bsd.tb_bg') or (defaults.get('res_model_id') and self.env['ir.model'].sudo().browse(defaults['res_model_id']).model == 'bsd.tb_bg'):
                defaults['bsd_tb_nt_id'] = defaults['res_id']
        # sync res_model / res_id to thông báo nghiệm thu id
        if 'bsd_tb_nt_id' not in defaults and defaults.get('res_id') and (defaults.get('res_model') or defaults.get('res_model_id')):
            if (defaults.get('res_model') and defaults['res_model'] == 'bsd.tb_bg') or (defaults.get('res_model_id') and self.env['ir.model'].sudo().browse(defaults['res_model_id']).model == 'bsd.tb_nt'):
                defaults['bsd_tb_nt_id'] = defaults['res_id']
        return defaults

    def _compute_is_highlighted(self):
        for event in self:
            event.is_highlighted = False
        super(CalendarEvent, self)._compute_is_highlighted()
        if self.env.context.get('active_model') == 'bsd.tb_bg':
            bsd_tb_bg_id = self.env.context.get('active_id')
            for event in self:
                if event.bsd_tb_bg_id.id == bsd_tb_bg_id:
                    event.is_highlighted = True
                else:
                    event.is_highlighted = False
        if self.env.context.get('active_model') == 'bsd.tb_nt':
            bsd_tb_nt_id = self.env.context.get('active_id')
            for event in self:
                if event.bsd_tb_nt_id.id == bsd_tb_nt_id:
                    event.is_highlighted = True
                else:
                    event.is_highlighted = False

    bsd_tb_bg_id = fields.Many2one('bsd.tb_bg', 'TB bàn giao')
    bsd_tb_nt_id = fields.Many2one('bsd.tb_nt', 'TB nghiệm thu')

    @api.model
    def create(self, vals):
        event = super(CalendarEvent, self).create(vals)

        if event.bsd_tb_bg_id and not event.activity_ids:
            event.bsd_tb_bg_id.log_meeting(event.name, event.start, event.duration)
        if event.bsd_tb_nt_id and not event.activity_ids:
            event.bsd_tb_nt_id.log_meeting(event.name, event.start, event.duration)
        return event
