# -*- coding:utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError
from odoo.tools.float_utils import float_round
import logging
_logger = logging.getLogger(__name__)


class BsdThongBaoNghiemThu(models.Model):
    _name = 'bsd.tb_nt'
    _description = "Thông báo nghiệm thu"
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _rec_name = 'bsd_ma_tb'
    _order = 'bsd_ngay_tao_tb desc'

    bsd_ma_tb = fields.Char(string="Mã", help="Mã thông báo nghiệm thu", required=True, readonly=True,
                            copy=False, default='/')
    _sql_constraints = [
        ('bsd_ma_tb_unique', 'unique (bsd_ma_tb)',
         'Mã thông báo đã tồn tại !')
    ]
    bsd_ngay_tao_tb = fields.Date(string="Ngày thông báo", help="Ngày tạo thông báo nghiệm thu",
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
                                          readonly=True,
                                          states={'nhap': [('readonly', False)]})
    bsd_ngay_nt = fields.Date(string="Ngày nghiệm thu", help="Ngày nghiệm thu",
                                     readonly=True,
                                     states={'nhap': [('readonly', False)]})
    # bsd_ngay_tb = fields.Date(string="Ngày thông báo", help="Ngày thông báo nghiệm thu",
    #                                  readonly=True,
    #                                  states={'nhap': [('readonly', False)]})
    bsd_ngay_ut = fields.Date(string="Ngày ước tính", help="Ngày ước tính",
                              readonly=True,
                              states={'nhap': [('readonly', False)]})
    bsd_ngay_in = fields.Datetime(string="Ngày in", help="Ngày in thông báo nghiệm thu", readonly=True)
    bsd_nguoi_in_id = fields.Many2one("res.users", string="Người in", help="Người in thông báo nghiệm thu",
                                      readonly=True)
    bsd_ngay_gui = fields.Date(string="Ngày gửi", help="Ngày gửi nghiệm thu", readonly=True)
    bsd_ngay_dong = fields.Date(string="Ngày đóng", help="Ngày đóng nghiệm thu", readonly=True)
    bsd_du_an_id = fields.Many2one('bsd.du_an', string="Dự án", help="Dự án", required=True,
                                   readonly=True,
                                   states={'nhap': [('readonly', False)]})
    bsd_unit_id = fields.Many2one('product.product', string="Sản phẩm", help="Sản phẩm", required=True,
                                  readonly=True,
                                  states={'nhap': [('readonly', False)]})
    bsd_hd_ban_id = fields.Many2one('bsd.hd_ban', string="Hợp đồng", help="Hợp đồng", required=True,
                                    readonly=True,
                                    states={'nhap': [('readonly', False)]})
    bsd_khach_hang_id = fields.Many2one('res.partner', string="Khách hàng", help="Khách hàng", required=True,
                                        readonly=True,
                                        states={'nhap': [('readonly', False)]})
    bsd_nghiem_thu_id = fields.Many2one('bsd.nghiem_thu', string="Nghiệm thu trước", readonly=True)
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
    bsd_don_gia_pql = fields.Monetary(string="Đơn giá PQL", help="Đơn giá phí quản lý được quy định trên sản phẩm",
                                      readonly=True,
                                      states={'nhap': [('readonly', False)]})
    bsd_tien_lp = fields.Monetary(string="Tiền phạt chậm TT", help="Tiền phạt chậm thanh toán của hợp đồng",
                                  readonly=True,
                                  states={'nhap': [('readonly', False)]})
    bsd_tien_lp_ut = fields.Monetary(string="Tiền phạt ước tính", help="Tiền phạt chậm thanh toán của hợp đồng",
                                     readonly=True,
                                     states={'nhap': [('readonly', False)]})
    bsd_so_ngay_tre = fields.Integer(string="Số ngày trễ", help="Số ngày trễ được tính từ ngày ước tính",
                                     readonly=True,
                                     states={'nhap': [('readonly', False)]})
    bsd_tong_tien = fields.Monetary(string="Tổng tiền", help="Tổng tiền phải thanh toán bao gồm ước tính lãi phạt",
                                    compute='_compute_tong_tien')

    @api.depends('bsd_tien_ng', 'bsd_tien_pbt', 'bsd_tien_pql', 'bsd_tien_lp', 'bsd_tien_lp_ut')
    def _compute_tong_tien(self):
        for each in self:
            each.bsd_tong_tien = each.bsd_tien_ng + each.bsd_tien_pbt + \
                                 each.bsd_tien_pql + each.bsd_tien_lp + each.bsd_tien_lp_ut
    company_id = fields.Many2one('res.company', string='Công ty', default=lambda self: self.env.company)
    currency_id = fields.Many2one(related="company_id.currency_id", string="Tiền tệ", readonly=True)
    state = fields.Selection([('nhap', 'Nháp'),
                              ('xac_nhan', 'Xác nhận'),
                              ('hoan_thanh', 'Hoàn thành'),
                              ('huy', 'Hủy')],
                             string="Trạng thái", default="nhap", required=True, readonly=True, tracking=1)
    bsd_so_nt = fields.Integer(string="# Ngiệm thu", compute="_compute_nt")
    meeting_count = fields.Integer('# Meetings', compute='_compute_meeting_count')

    def _compute_meeting_count(self):
        meeting_data = self.env['calendar.event'].read_group([('bsd_tb_nt_id', 'in', self.ids)], ['bsd_tb_nt_id'], ['bsd_tb_nt_id'])
        mapped_data = {m['bsd_tb_nt_id'][0]: m['bsd_tb_nt_id_count'] for m in meeting_data}
        for lead in self:
            lead.meeting_count = mapped_data.get(lead.id, 0)
    
    def _compute_nt(self):
        for each in self:
            nghiem_thu = self.env['bsd.nghiem_thu'].search([('bsd_tb_nt_id', '=', self.id)])
            each.bsd_so_nt = len(nghiem_thu)

    def action_view_nghiem_thu(self):
        action = self.env.ref('bsd_dich_vu.bsd_nghiem_thu_action').read()[0]

        nghiem_thu = self.env['bsd.nghiem_thu'].search([('bsd_tb_nt_id', '=', self.id)])
        if len(nghiem_thu) > 1:
            action['domain'] = [('id', 'in', nghiem_thu.ids)]
        elif nghiem_thu:
            form_view = [(self.env.ref('bsd_dich_vu.bsd_nghiem_thu_form').id, 'form')]
            if 'views' in action:
                action['views'] = form_view + [(state, view) for state, view in action['views'] if view != 'form']
            else:
                action['views'] = form_view
            action['res_id'] = nghiem_thu.id
        # Prepare the context.
        context = {
            'default_bsd_tb_nt_id': self.id,
        }
        action['context'] = context
        return action

    # DV.21.01 Xác nhận thông báo nghiêm thu
    def action_xac_nhan(self):
        if self.state == 'nhap':
            self.write({
                'state': 'xac_nhan'
            })

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

    # DV.21.02 In thông báo nghiệm thu
    def action_in_tb(self):
        return self.env.ref('bsd_dich_vu.bsd_tb_nt_report_action').read()[0]

    # DV.21.03 Cập nhật ngày gửi
    def action_gui_tb(self):
        action = self.env.ref('bsd_dich_vu.bsd_wizard_tb_nt_action').read()[0]
        action['context'] = {'loai_ngay': 'ngay_gui'}
        _logger.debug(action)
        return action

    # DV.21.04 Cập nhật ngày đóng
    def action_dong_tb(self):
        action = self.env.ref('bsd_dich_vu.bsd_wizard_tb_nt_action').read()[0]
        action['context'] = {'loai_ngay': 'ngay_dong'}
        return action

    # DV.21.05 Hủy thông báo nghiệm thu
    def action_huy(self):
        if self.state in ['nhap', 'xac_nhan']:
            self.write({
                'state': 'huy'
            })

    # DV.21.06 Tự động tạo nghiệm thu sản phẩm
    def tao_nt_sp(self):
        phi_ps = self.env['bsd.phi_ps'].search([('bsd_nghiem_thu_id', '=', self.bsd_nghiem_thu_id.id)], limit=1)
        self.env['bsd.nghiem_thu'].create({
            'bsd_ngay_tao_nt': fields.Datetime.now(),
            'bsd_tb_nt_id': self.id,
            'bsd_du_an_id': self.bsd_du_an_id.id,
            'bsd_khach_hang_id': self.bsd_khach_hang_id.id,
            'bsd_hd_ban_id': self.bsd_hd_ban_id.id,
            'bsd_unit_id': self.bsd_unit_id.id,
            'bsd_nghiem_thu_id': self.bsd_nghiem_thu_id.id,
            'bsd_phi_ps_id': phi_ps.id,
            'state': 'nhap',
        })

    @api.model
    def create(self, vals):
        sequence = False
        if 'bsd_du_an_id' in vals:
            du_an = self.env['bsd.du_an'].browse(vals['bsd_du_an_id'])
            sequence = du_an.get_ma_bo_cn(loai_cn=self._name)
        if not sequence:
            raise UserError(_('Dự án chưa có mã thông báo nghiệm thu.'))
        vals['bsd_ma_tb'] = sequence.next_by_id()
        return super(BsdThongBaoNghiemThu, self).create(vals)

    # Hẹn ngày gặp khách hàng
    def action_schedule_meeting(self):
        """ Open meeting's calendar view to schedule meeting on current opportunity.
            :return dict: dictionary value for created Meeting view
        """
        self.ensure_one()
        action = self.env.ref('calendar.action_calendar_event').read()[0]
        partner_ids = self.env.user.partner_id.ids
        if self.bsd_khach_hang_id:
            partner_ids.append(self.bsd_khach_hang_id.id)
        action['context'] = {
            'default_bsd_tb_nt_id': self.id,
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
