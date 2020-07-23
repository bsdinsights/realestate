# -*- coding:utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError
import logging
_logger = logging.getLogger(__name__)


class BsdNghiemThu(models.Model):
    _name = 'bsd.nghiem_thu'
    _description = "Nghiệm thu"
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _rec_name = 'bsd_ma_nt'

    bsd_ma_nt = fields.Char(string="Mã", help="Mã nghiệm thu", required=True, readonly=True,
                            copy=False, default='/')
    _sql_constraints = [
        ('bsd_ma_nt_unique', 'unique (bsd_ma_nt)',
         'Mã nghiệm thu đã tồn tại !')
    ]
    bsd_ngay_tao_nt = fields.Datetime(string="Ngày", help="Ngày tạo nghiệm thu",
                                      required=True, default=lambda self: fields.Datetime.now(),
                                      readonly=True,
                                      states={'nhap': [('readonly', False)]})
    bsd_tb_nt_id = fields.Many2one('bsd.tb_nt', string="TB nghiệm thu", required=True,
                                   help="Thông báo nghiệm thu",
                                   readonly=True,
                                   states={'nhap': [('readonly', False)]})
    bsd_loai = fields.Selection([('dat', 'Đạt'), ('khong_dat', 'Không đạt')], help="Kết quả nghiệm thu",
                                string="Loại kết quả", required=True, default='dat',
                                readonly=True,
                                states={'nhap': [('readonly', False)]})
    bsd_yc_sc = fields.Boolean(string="Yêu cầu sửa chữa",
                               help="Đánh dấu kết quả nghiệm thu có yêu cầu sửa chữa hay không",
                               readonly=True,
                               states={'nhap': [('readonly', False)]})
    bsd_dien_giai = fields.Char(string="Diễn giải", help="Diễn giải",
                                readonly=True,
                                states={'nhap': [('readonly', False)]})
    bsd_duyet_yc = fields.Selection([('co', 'Đồng ý sửa chữa'), ('khong', 'Từ chối sửa chữa')], default='co',
                                    string="Duyệt yêu cầu", help="Kết quả yêu cầu sửa chữa",
                                    readonly=True,
                                    states={'nhap': [('readonly', False)]})
    bsd_ly_do = fields.Char(string="Lý do từ chối", help="Lý do Ban quản lý dự án từ chối yêu cầu sửa chữa",
                                   readonly=True,
                                   states={'nhap': [('readonly', False)]})
    bsd_so_ngay_sc = fields.Integer(string="Thời gian sửa chữa", help="Thời gian sửa chữa do Ban quản lý dự án cung cấp",
                                    readonly=True,
                                    states={'nhap': [('readonly', False)]})
    bsd_ngay_nt_lai = fields.Date(string="Ngày nghiệm thu lại", help="Ngày nghiệm thu lại",
                                  readonly=True,
                                  states={'nhap': [('readonly', False)]})
    bsd_co_pps = fields.Boolean(string="Phí phát sinh", help="Sửa chữa có phát sinh chi phí",
                                readonly=True,
                                states={'nhap': [('readonly', False)]})
    bsd_tien_ps = fields.Monetary(string="Chi phí phát sinh", help="Chi phí phát sinh từ yêu cầu sửa chữa",
                                  readonly=True,
                                  states={'nhap': [('readonly', False)]})
    bsd_dot_tt_id = fields.Many2one('bsd.lich_thanh_toan', string="Đợt thanh toán", readonly=True,
                                    help="""Đợt thanh toán được yêu cầu thanh toán 
                                            thêm phí phát sinh từ yêu cầu sửa chữa""")
    bsd_ngay_kt_xn = fields.Datetime(string="Xác nhận PPS", help="Ngày kế toán xác nhận phí phát sinh", readonly=True)
    bsd_ngay_in_bb = fields.Datetime(string="Ngày in biên bản", help="Ngày in biên bản nghiệm thu theo loại kết quả",
                                     readonly=True)
    bsd_ngay_nt_tt = fields.Datetime(string="Ngày nghiệm thu", help="Ngày thực hiện nghiệm thu",
                                     readonly=True,
                                     states={'nhap': [('readonly', False)]})
    bsd_nguoi_nt_id = fields.Many2one("hr.employee", help="Người thực hiện nghiệm thu",
                                      readonly=True,
                                      states={'nhap': [('readonly', False)]},
                                      string="Người nghiệm thu")
    bsd_du_an_id = fields.Many2one(related='bsd_tb_nt_id.bsd_du_an_id', store=True)
    bsd_unit_id = fields.Many2one(related='bsd_tb_nt_id.bsd_unit_id', store=True)
    bsd_hd_ban_id = fields.Many2one(related='bsd_tb_nt_id.bsd_hd_ban_id', store=True)
    bsd_khach_hang_id = fields.Many2one(related='bsd_tb_nt_id.bsd_khach_hang_id', store=True)
    bsd_tien_ng = fields.Monetary(related='bsd_tb_nt_id.bsd_tien_ng')
    bsd_tien_pbt = fields.Monetary(related='bsd_tb_nt_id.bsd_tien_pbt')
    bsd_tien_pql = fields.Monetary(related='bsd_tb_nt_id.bsd_tien_pql')
    bsd_thang_pql = fields.Integer(related='bsd_tb_nt_id.bsd_thang_pql')
    bsd_don_gia_pql = fields.Monetary(related='bsd_tb_nt_id.bsd_don_gia_pql')
    company_id = fields.Many2one('res.company', string='Công ty', default=lambda self: self.env.company)
    currency_id = fields.Many2one(related="company_id.currency_id", string="Tiền tệ", readonly=True)
    state = fields.Selection([('nhap', 'Nháp'), ('xac_nhan_tt', 'Xác nhận thông tin'),
                              ('xac_nhan', 'Xác nhận'), ('dong_nt', 'Đóng nghiệm thu'),
                              ('huy', 'Hủy')],
                             string="Trạng thái", default="nhap", required=True, readonly=True, tracking=1)
    bsd_ly_do_huy = fields.Char(string="Lý do hủy", readonly=True, tracking=2)

    @api.onchange('bsd_loai')
    def _onchange_loai(self):
        if self.bsd_loai == 'dat':
            self.bsd_yc_sc = False
        else:
            self.bsd_yc_sc = True

    @api.onchange('bsd_duyet_yc')
    def _onchange_duyet(self):
        self.bsd_co_pps = False

    # DV.10.01 Xác nhận nghiệm thu
    def action_xac_nhan(self):
        # Kiểm tra sản phẩm nghiệm thu
        kiem_tra = self._kiem_tra_nt()
        if isinstance(kiem_tra, dict):
            return kiem_tra
        else:
            if self.state == 'nhap':
                if self.bsd_co_pps:
                    self.write({
                        'state': 'xac_nhan_tt',
                    })
                else:
                    self.write({
                        'state': 'xac_nhan',
                    })

    # DV.10.02 Phí phát sinh
    def action_phi_ps(self):
        # Kiểm tra sản phẩm nghiệm thu
        kiem_tra = self._kiem_tra_nt()
        if isinstance(kiem_tra, dict):
            return kiem_tra
        else:
            action = self.env.ref('bsd_dich_vu.bsd_wizard_nghiem_thu_action').read()[0]
            return action

    # DV.10.03 In biên bản
    def action_in_bb(self):
        action = self.env.ref('bsd_dich_vu.bsd_nghiem_thu_report_action').read()[0]
        return action

    # DV.10.04 Đóng nghiệm thu
    def action_dong_nt(self):
        # Kiểm tra sản phẩm nghiệm thu
        kiem_tra = self._kiem_tra_nt()
        if isinstance(kiem_tra, dict):
            return kiem_tra
        else:
            self._tao_tb_nt()
            self._tao_dot_thu_pps()

    # DV.10.05 Hủy nghiệm thu
    def action_huy(self):
        action = self.env.ref('bsd_dich_vu.bsd_wizard_huy_nt_action').read()[0]
        return action

    # DV.10.06 Tạo thông báo nghiệm thu
    def _tao_tb_nt(self):
        pass

    # DV.10.07 Kiểm tra điều kiện nghiệm thu sản phẩm
    def _kiem_tra_nt(self):
        # Kiểm tra hợp đồng
        if self.bsd_hd_ban_id.state == 'thanh_ly':
            if self.state in ['nhap', 'xac_nhan_tt', 'xac_nhan']:
                self.write({
                    'state': 'huy',
                    'bsd_ly_do_huy': 'Hợp đồng đã bị thanh lý'
                })
            message_id = self.env['message.wizard'].create(
                {'message': _('Hợp đồng đã bị thanh lý. Vui lòng kiểm tra lại thông tin')})
            _logger.debug("kiểm tra hd")
            return {
                'name': _('Thông báo'),
                'type': 'ir.actions.act_window',
                'view_mode': 'form',
                'res_model': 'message.wizard',
                'res_id': message_id.id,
                'target': 'new'
            }
        if not self.bsd_unit_id.bsd_ngay_bg:
            if self.state in ['nhap', 'xac_nhan_tt', 'xac_nhan']:
                self.write({
                    'state': 'huy',
                    'bsd_ly_do_huy': "Sản phẩm đã được bàn giao"
                })
            message_id = self.env['message.wizard'].create(
                {'message': _('Sản phẩm đã được bàn giao. Vui lòng kiểm tra lại thông tin')})
            _logger.debug("kiểm tra nt")
            return {
                'name': _('Thông báo'),
                'type': 'ir.actions.act_window',
                'view_mode': 'form',
                'res_model': 'message.wizard',
                'res_id': message_id.id,
                'target': 'new'
            }
        return True

    # DV.10.08 Tự động đính kèm phí phát sinh vào đợt thanh toán
    def _tao_dot_thu_pps(self):
        pass

    @api.model
    def create(self, vals):
        sequence = False
        if 'bsd_tb_nt_id' in vals:
            tb_nt = self.env['bsd.tb_nt'].browse(vals['bsd_tb_nt_id'])
            sequence = tb_nt.bsd_du_an_id.get_ma_bo_cn(loai_cn=self._name)
        if not sequence:
            raise UserError(_('Dự án chưa có mã nghiệm thu'))
        vals['bsd_ma_nt'] = sequence.next_by_id()
        return super(BsdNghiemThu, self).create(vals)