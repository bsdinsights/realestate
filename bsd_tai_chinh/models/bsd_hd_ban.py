# -*- coding:utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError
import logging
_logger = logging.getLogger(__name__)


class BsdHdBan(models.Model):
    _inherit = 'bsd.hd_ban'

    bsd_tl_tt_hd = fields.Float(string="Tỷ lệ thanh toán HĐ", help="Tỷ lệ thanh toán hợp đồng", compute='_compute_tl_tt',
                                store=True, digits=(10, 1))
    bsd_tien_tt_hd = fields.Monetary(string="Tiền thanh toán HĐ", help="Tiền thanh toán hợp đồng",
                                     compute='_compute_tl_tt', store=True)
    bsd_no_goc = fields.Monetary(string="Nợ gốc", compute='_compute_tl_tt', store=True,
                                 help="Trường thông tin nợ gốc của hợp đồng dùng khi thông báo nợ gốc cho khách hàng")

    bsd_phi_ps_ids = fields.One2many('bsd.phi_ps', 'bsd_hd_ban_id', string="Phí phát sinh", readonly=True)
    bsd_lai_phat_ids = fields.One2many('bsd.lai_phat', 'bsd_hd_ban_id', string="Lãi phạt", readonly=True)
    bsd_lt_phai_tt = fields.Monetary(string="Tiền phạt phải TT", compute='_compute_lp_tt', store=True)

    bsd_phieu_thu_ids = fields.One2many('bsd.phieu_thu', 'bsd_hd_ban_id', string="Thanh toán", readonly=True)
    bsd_so_mg = fields.Integer(string="# Miễn giảm", compute='_compute_so_mg')

    def _compute_so_mg(self):
        for each in self:
            mien_giam = self.env['bsd.mien_giam'].search([('bsd_hd_ban_id', '=', self.id)])
            each.bsd_so_mg = len(mien_giam)

    def action_view_mg(self):
        action = self.env.ref('bsd_tai_chinh.bsd_mien_giam_action').read()[0]

        mien_giam = self.env['bsd.mien_giam'].search([('bsd_hd_ban_id', '=', self.id)])
        if len(mien_giam) > 1:
            action['domain'] = [('id', 'in', mien_giam.ids)]
        elif mien_giam:
            form_view = [(self.env.ref('bsd_tai_chinh.bsd_mien_giam_form').id, 'form')]
            if 'views' in action:
                action['views'] = form_view + [(state, view) for state, view in action['views'] if view != 'form']
            else:
                action['views'] = form_view
            action['res_id'] = mien_giam.id
        return action

    @api.depends('bsd_lai_phat_ids', 'bsd_lai_phat_ids.bsd_tien_phai_tt')
    def _compute_lp_tt(self):
        for each in self:
            each.bsd_lt_phai_tt = sum(each.bsd_lai_phat_ids.mapped('bsd_tien_phai_tt'))

    @api.depends('bsd_ltt_ids.bsd_tien_da_tt', 'bsd_tong_gia')
    def _compute_tl_tt(self):
        for each in self:
            if each.bsd_tong_gia > 0 and each.bsd_ltt_ids:
                each.bsd_tien_tt_hd = sum(each.bsd_ltt_ids.mapped('bsd_tien_da_tt')) + \
                                      each.bsd_ltt_ids.filtered(lambda x: x.bsd_stt == 1).bsd_tien_dc
                each.bsd_tl_tt_hd = each.bsd_tien_tt_hd / (each.bsd_tong_gia - each.bsd_tien_pbt) * 100
                each.bsd_no_goc = sum(each.bsd_ltt_ids.filtered(lambda l: l.bsd_ma_dtt != 'DBGC')
                                      .mapped('bsd_tien_phai_tt'))
            else:
                each.bsd_tien_tt_hd = 0
                each.bsd_tl_tt_hd = 0

    # DV.01.13 Theo dõi giao dịch khuyến mãi
    def tao_giao_dich_khuyen_mai(self, ngay_tt):
        ngay_tt = ngay_tt.date()
        # Các khuyến mãi có điều kiện của hợp đồng
        km_hd = self.bsd_dot_mb_id.bsd_km_ids\
            .filtered(lambda k: k.bsd_loai != 'khong')
        # Kiểm tra khuyến mãi của hợp đồng đã tạo khuyến mãi
        km_da_ps_gd = self.env['bsd.ps_gd_km'].search([('bsd_hd_ban_id', '=', self.id)]).mapped('bsd_khuyen_mai_id')
        # Các khuyến mãi chưa tạo giao dịch
        km_ids = km_hd - km_da_ps_gd
        # Kiểm tra thời điểm thanh toán nằm trong khuyến mãi
        km_ids = km_ids.filtered(lambda k: k.bsd_tu_ngay <= ngay_tt <= k.bsd_den_ngay)
        # Lấy ngày thanh toán đặc cọc
        if self.bsd_dat_coc_id.bsd_ngay_tt:
            ngay_tt_dc = self.bsd_dat_coc_id.bsd_ngay_tt.date()
            for km_check_dc in km_ids.filtered(lambda k: k.bsd_ngay_hldc):
                # Kiểm tra ngày thanh toán đặc cọc
                if ngay_tt_dc > km_check_dc.bsd_ngay_hldc:
                    continue
                if km_check_dc.bsd_loai == 'tien':
                    if self.bsd_tien_tt_hd < km_check_dc.bsd_tong_tt:
                        continue
                if km_check_dc.bsd_loai == 'ty_le':
                    if self.bsd_tl_tt_hd < km_check_dc.bsd_tl_tt:
                        continue
                if km_check_dc.bsd_loai == 'ty_le_tien':
                    if self.bsd_tien_tt_hd < km_check_dc.bsd_tong_tt and self.bsd_tl_tt_hd < km_check_dc.bsd_tl_tt:
                        continue
                self.env['bsd.ps_gd_km'].create({
                    'bsd_khuyen_mai_id': km_check_dc.id,
                    'bsd_hd_ban_id': self.id,
                    'bsd_khach_hang_id': self.bsd_khach_hang_id.id,
                    'bsd_ngay_tt': ngay_tt,
                    'state': 'xac_nhan',
                })
        for km in km_ids.filtered(lambda k: not k.bsd_ngay_hldc):
            if km.bsd_loai == 'tien':
                if self.bsd_tien_tt_hd < km.bsd_tong_tt:
                    continue
            if km.bsd_loai == 'ty_le':
                if self.bsd_tl_tt_hd < km.bsd_tl_tt:
                    continue
            if km.bsd_loai == 'ty_le_tien':
                if self.bsd_tien_tt_hd < km.bsd_tong_tt and self.bsd_tl_tt_hd < km.bsd_tl_tt:
                    continue
            self.env['bsd.ps_gd_km'].create({
                'bsd_khuyen_mai_id': km.id,
                'bsd_hd_ban_id': self.id,
                'bsd_khach_hang_id': self.bsd_khach_hang_id.id,
                'bsd_ngay_tt': ngay_tt,
                'state': 'xac_nhan',
            })

    # DV.01.15 - Cập nhật trạng thái Thanh toán đợt 1
    def action_tt_dot1(self):
        if self.state == '01_ht_dc' and not self.bsd_duyet_db:
            self.write({
                'state': '02_tt_dot1'
            })
            # Cập nhật trạng thái sản phẩm
            self.bsd_unit_id.sudo().write({
                'state': 'tt_dot_1'
            })

    # DV.01.16 - Cập nhật trạng thái Đủ điều kiện
    def action_du_dk(self):
        # Kiểm tra nếu hợp đồng có duyệt đặc biệt thì ko cập nhật trạng thái đủ dk
        if self.bsd_duyet_db:
            return
        if self.state in ['02_tt_dot1', '03_da_ky_ttdc']:
            self.write({
                'state': '04_du_dk'
            })
            # Cập nhật trạng thái sản phẩm
            self.bsd_unit_id.sudo().write({
                'state': 'du_dk'
            })

    # DV.01.21 Cập nhật trạng thái Đang thanh toán
    def action_dang_tt(self):
        # Kiểm tra nếu hợp đồng có duyệt bàn giao đặc biệt thì không cập nhật trạng thái hợp đồng
        if self.bsd_duyet_bgdb:
            return
        # Lấy đợt thanh toán ký hợp đồng
        dot_ky_hd = self.bsd_ltt_ids.filtered(lambda l: l.bsd_dot_ky_hd)
        # Lấy đợt dự ký bàn giao
        dot_dkbg = self.bsd_ltt_ids.filtered(lambda l: l.bsd_ma_dtt == 'DKBG')
        dot_sau_ky_hd = self.bsd_ltt_ids.filtered(lambda l: dot_ky_hd.bsd_stt < l.bsd_stt < dot_dkbg.bsd_stt)
        # Lấy đợt thanh toán sau ký hợp đồng
        dot_state = dot_sau_ky_hd.mapped('bsd_thanh_toan')
        if self.state == '05_da_ky' and 'da_tt' in dot_state:
            self.write({
                'state': '06_dang_tt'
            })

    # DV.01.22 Cập nhật trạng thái đủ điều kiện bàn giao
    def action_du_dkbg(self):
        # Kiểm tra nếu hợp đồng có duyệt bàn giao đặt biệt thì không cập nhật trạng thái hợp đồng
        if self.bsd_duyet_bgdb:
            return
        # Kiểm tra hợp đông đã được thanh toán phí bảo trì
        if not self.bsd_dot_pbt_ids:
            raise UserError(_('Hợp đồng chưa ghi nhận thu phí bảo trì.'))
        if len(self.bsd_dot_pbt_ids) > 1:
            raise UserError(_('Hợp đồng có nhiều hơn 1 đợt thu phí bảo trì.'))
        if self.bsd_dot_pbt_ids.bsd_thanh_toan != 'da_tt':
            return
        # Kiểm tra hợp đông đã được thanh toán phí quản lý
        if not self.bsd_dot_pql_ids:
            raise UserError(_('Hợp đồng chưa ghi nhận thu phí quản lý.'))
        if len(self.bsd_dot_pql_ids) > 1:
            raise UserError(_('Hợp đồng có nhiều hơn 1 đợt thu phí quản lý.'))
        if self.bsd_dot_pql_ids.bsd_thanh_toan != 'da_tt':
            return
        # Kiểm tra hợp đồng đã thanh toán đợt dự kiến bàn giao
        dot_dkbg = self.bsd_ltt_ids.filtered(lambda l: l.bsd_ma_dtt == 'DKBG')
        if not dot_dkbg:
            raise UserError(_("Hợp đồng không có đợt dự kiến bàn giao."))
        if len(dot_dkbg) > 1:
            raise UserError(_("Hợp đồng có nhiều hơn 1 đợt dkbg."))
        if dot_dkbg.bsd_thanh_toan != 'da_tt':
            return
        # Kiểm tra các phí phát sinh từ đợt dkbg trở về trước
        dot_tt_truoc_bg = self.bsd_ltt_ids.filtered(lambda d: d.bsd_stt <= dot_dkbg.bsd_stt)
        # Lấy các phí phát sinh
        phi_ps_ids = self.env['bsd.phi_ps'].search([('bsd_hd_ban_id', '=', self.id),
                                                    ('bsd_dot_tt_id', 'in', dot_tt_truoc_bg.ids),
                                                    ('state', '=', 'ghi_so')])
        phi_ps_ids = phi_ps_ids.filtered(lambda p: p.bsd_thanh_toan != 'da_tt')
        if phi_ps_ids:
            return

        # Kiểm tra khách hàng đã thanh toán hết tiền phạt chậm tt hay chưa
        # Lấy các tiền phạt chậm thanh toán của các đợt thanh toán
        lai_phat_ids = self.env['bsd.lai_phat'].search([('bsd_hd_ban_id', '=', self.id),
                                                        ('bsd_dot_tt_id', 'in', dot_tt_truoc_bg.ids),
                                                        ('state', '=', 'hieu_luc')])
        lai_phat_ids = lai_phat_ids.filtered(lambda p: p.bsd_thanh_toan != 'da_tt')
        if lai_phat_ids:
            return
        # Kiểm tra tỷ lệ thanh toán của hợp đồng với điều kiện bàn giao trên sản phẩm
        if self.bsd_tl_tt_hd < self.bsd_unit_id.bsd_dk_bg:
            return
        # Ghi nhận trạng thái đủ dk bàn giao
        self.write({
            'state': '07_du_dkbg'
        })

    # DV.01.23 Cập nhật trạng thái hoàn tất thanh toán
    def action_ht_tt(self):
        # Kiểm tra đã thu đủ nợ gốc chưa
        if self.bsd_ltt_ids.filtered(lambda l: l.bsd_thanh_toan != 'da_tt'):
            return
        # Kiểm tra đã thu phí bảo trì chưa
        if self.bsd_dot_pbt_ids.filtered(lambda p: p.bsd_thanh_toan != 'da_tt'):
            return
        # Kiểm tra đã thu phí quản lý chưa
        if self.bsd_dot_pql_ids.filtered(lambda p: p.bsd_thanh_toan != 'da_tt'):
            return
        # Kiểm tra đã thu đủ phí phát sinh chưa
        if self.bsd_phi_ps_ids.filtered(lambda p: p.bsd_thanh_toan != 'da_tt'):
            return
        # Kiểm tra đã thu đủ tiền phạt chưa
        if self.bsd_lai_phat_ids.filtered(lambda p: p.bsd_thanh_toan != 'da_tt'):
            return

        # Cập nhật trạng thái hoàn tất thanh toán
        self.write({
            'state': '09_ht_tt'
        })

    # Tạo thanh toán
    def action_thanh_toan(self):
        _logger.debug(self.id)
        wizard_tt = self.env['bsd.wizard.tt_hd'].create({
            'bsd_tien_kh': 0,
            'bsd_hd_ban_id': self.id,
            'bsd_khach_hang_id': self.bsd_khach_hang_id.id,
            'bsd_du_an_id': self.bsd_du_an_id.id,
            'bsd_unit_id': self.bsd_unit_id.id,
        })
        _logger.debug("tạo thanh toán1")
        for dot_tt in self.bsd_ltt_ids\
                .filtered(lambda x: (x.bsd_thanh_toan != 'da_tt' or x.bsd_tien_phat > 0) and x.bsd_ngay_hh_tt)\
                .sorted('bsd_stt'):
            self.env['bsd.wizard.ct_dot'].create({
                'bsd_dot_tt_id': dot_tt.id,
                'bsd_wizard_tt_id': wizard_tt.id
            })
        _logger.debug("tạo thanh toán2")
        # Kiểm tra sản phẩm đã có ngày chứng nhận cất nóc mới thu dc pql,pbt
        if self.bsd_unit_id.bsd_ngay_cn:
            for phi in (self.bsd_dot_pbt_ids + self.bsd_dot_pql_ids):
                self.env['bsd.wizard.ct_phi'].create({
                    'bsd_phi_tt_id': phi.id,
                    'bsd_wizard_tt_id': wizard_tt.id
                })
        _logger.debug("tạo thanh toán3")
        for pps in self.bsd_phi_ps_ids:
            self.env['bsd.wizard.ct_pps'].create({
                'bsd_pps_id': pps.id,
                'bsd_wizard_tt_id': wizard_tt.id
            })
        _logger.debug("tạo thanh toán4")
        for dot_tt in self.bsd_ltt_ids\
                .filtered(lambda x: x.bsd_tien_phat > 0 and x.bsd_ngay_hh_tt)\
                .sorted('bsd_stt'):
            self.env['bsd.wizard.ct_lp'].create({
                'bsd_dot_tt_id': dot_tt.id,
                'bsd_wizard_tt_id': wizard_tt.id
            })
        _logger.debug("tạo thanh toán5")
        action = self.env.ref('bsd_tai_chinh.bsd_wizard_tt_dot_action').read()[0]
        action['res_id'] = wizard_tt.id
        _logger.debug("tạo thanh toán6")
        _logger.debug(action)
        return action

    def action_uoc_tinh_lp(self):
        action = self.env.ref('bsd_tai_chinh.bsd_wizard_uoc_tinh_lp_action').read()[0]
        return action

    def action_mien_giam(self):
        action = self.env.ref('bsd_tai_chinh.bsd_mien_giam_action_popup').read()[0]
        action['context'] = {'default_bsd_hd_ban_id': self.id,
                             'default_bsd_ten': 'Miễn giảm hợp đồng ' + self.bsd_ma_hd_ban,
                             'default_bsd_du_an_id': self.bsd_du_an_id.id,
                             'default_bsd_unit_id': self.bsd_unit_id.id,
                             'default_bsd_khach_hang_id': self.bsd_khach_hang_id.id}
        return action