# -*- coding:utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError


class BsdMaBoChungTu(models.Model):
    _name = 'bsd.ma_bo_cn'
    _description = "Cách đánh mã bộ chứng từ cho từng dự án"
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _rec_name = 'bsd_ten_cn'
    _order = 'bsd_loai_cn'

    bsd_ten_cn = fields.Char(string="Tên", help="Tên bộ chứng từ", required=True,
                             readonly=True,
                             states={'nhap': [('readonly', False)]})
    bsd_du_an_id = fields.Many2one('bsd.du_an', string="Dự án", help="Dự án", required=True,
                                   readonly=True,
                                   states={'nhap': [('readonly', False)]})
    bsd_loai_cn = fields.Selection([('bsd.gc_tc', 'Giữ chỗ thiện chí'),
                                    ('bsd.phieu_thu', 'Thanh toán'),
                                    ('bsd.huy_gc', 'Hủy giữ chỗ'),
                                    ('bsd.hoan_tien', 'Hoàn tiền'),
                                    ('bsd.gia_han_gc', 'Gia hạn giữ chỗ'),
                                    ('bsd.rap_can', 'Ráp căn'),
                                    ('bsd.giu_cho', 'Giữ chỗ'),
                                    ('bsd.chuyen_gc', 'Chuyển giữ chỗ'),
                                    ('bsd.chuyen_ut_gc', 'Chuyển độ ưu tiên giữ chỗ'),
                                    ('product.pricelist', 'Bảng giá'),
                                    ('bsd.lai_phat_tt', 'Lãi phạt chậm thanh toán'),
                                    ('bsd.cs_tt', 'Phương thức thanh toán'),
                                    ('bsd.dk_bg', 'Điều kiện bàn giao'),
                                    ('bsd.khuyen_mai', 'Khuyến mãi'),
                                    ('bsd.chiet_khau', 'Chiết khấu'),
                                    ('bsd.ck_ch', 'Chiết khấu chung'),
                                    ('bsd.ck_nb', 'Chiết khấu nội bộ'),
                                    ('bsd.ck_cstt', 'Chiết khấu Phương thức thanh toán'),
                                    ('bsd.ck_ms', 'Chiết khấu mua sỉ'),
                                    ('bsd.ck_ttn', 'Chiết khấu thanh toán nhanh'),
                                    ('bsd.ck_ttth', 'Chiết khấu thanh toán trước hạn'),
                                    ('bsd.ck_db', 'Chiết khấu đặc biệt'),
                                    ('bsd.ps_gd_ck', 'Chiết khấu giao dịch'),
                                    ('bsd.dot_mb', 'Đợt mở bán'),
                                    ('bsd.them_unit', 'Thêm sản phẩm vào đợt mở bán'),
                                    ('bsd.thu_hoi', 'Thu hồi sản phẩm'),
                                    ('bsd.bao_gia', 'Bảng tính giá'),
                                    ('bsd.dat_coc', 'Đặt cọc'),
                                    ('bsd.dat_coc.chuyen_dd', 'Thay đổi đại diện ký TTĐC/HĐMB'),
                                    ('bsd.dat_coc.td_tt', 'Thay đổi thông tin đặt cọc'),
                                    ('bsd.ds_td', 'Danh sách theo dõi'),
                                    ('bsd.tb_tl', 'Thông báo thanh lý'),
                                    ('bsd.thanh_ly', 'Thanh lý'),
                                    ('bsd.hd_ban', 'Hợp đồng'),
                                    ('bsd.hd_ban_cn', 'Chuyển nhượng hợp đồng'),
                                    ('bsd.tb_tt', 'Thông báo thanh toán'),
                                    ('bsd.tb_nn', 'Thông báo nhắc nợ'),
                                    ('bsd.cn_dkbg', 'Cập nhật dự kiến bàn giao'),
                                    ('bsd.cn_dttt', 'Cập nhật diện tích thực tế'),
                                    ('bsd.tb_nt', 'Thông báo nghiệm thu'),
                                    ('bsd.nghiem_thu', 'Nghiệm thu'),
                                    ('bsd.tb_bg', 'Thông báo bàn giao'),
                                    ('bsd.cn_ndc', 'Cập nhật ngày thanh toán cuối'),
                                    ('bsd.bg_sp', 'Bàn giao sản phẩm'),
                                    ('bsd.bg_gt', 'Bàn giao giấy tờ'),
                                    ('bsd.tl_kt_hd', 'Thanh lý kết thúc hợp đồng'),
                                    ('bsd.pl_dsh', 'Phụ lục đồng sở hữu'),
                                    ('bsd.pl_pttt', 'Phụ lục thay đổi PTTT'),
                                    ('bsd.pl_cktm', 'Phụ lục thay đổi CKTM'),
                                    ('bsd.pl_dkbg', 'Phụ lục thay đổi ĐKBG'),
                                    ('bsd.pl_qsdd', 'Phụ lục thay đổi QSDĐ'),
                                    ('bsd.pl_tti', 'Phụ lục thay đổi thông tin'),
                                    ('bsd.pl_cldt', 'Phụ lục điều chỉnh chênh lệch diện tích'),
                                    ('bsd.tb_kq_dttt', 'Thư thông báo kết quả đo đạt thực tế'),
                                    ('bsd.can_tru', 'Cấn trừ'),
                                    ('bsd.huy_tt', 'Hủy thanh toán'),
                                    ('bsd.hoa_hong', 'Hoa hồng'),
                                    ('bsd.phi_mg', 'Phí môi giới'),
                                    ('bsd.tinh_hoa_hong', 'Tính hoa hồng'),
                                    ('bsd.phi_ps', 'Phí phát sinh'),
                                    ('bsd.mien_giam', 'Miễn giảm thanh toán'),
                                    ('bsd.ps_gd_km', 'Khuyến mãi giao dịch'),
                                    ('bsd.vay_nh', 'Vay ngân hàng'),
                                    ('bsd.xn_dhs', 'Xác nhận đủ hồ sơ'),
                                    ('bsd.vp_hd', 'Vi phạm hợp đồng'),
                                    ('bsd.cn_htt', 'Cập nhật ngày đến hạn thanh toán')],
                                   string="Loại chứng từ", help="Loại chứng từ được đặt mã", required=True,
                                   readonly=True,
                                   states={'nhap': [('readonly', False)]})
    bsd_ma_cn = fields.Char(string="Mã tiền tố", help="Mã tiền tố của chứng từ", required=True,
                            readonly=True,
                            states={'nhap': [('readonly', False)]})
    _sql_constraints = [
        ('bsd_ma_cn_unique', 'unique (bsd_ma_cn)',
         'Mã tiền tố chứng từ đã tồn tại !'),
    ]
    bsd_ma_ht = fields.Char(string="Mã hậu tố", help="Mã hậu tố của chứng từ",
                            readonly=True,
                            states={'nhap': [('readonly', False)]})
    bsd_sl_ky_tu = fields.Integer(string="Độ dài chuỗi", help="Độ dài chuổi ký tự sinh tự động của hệ thống",
                                  required=True,
                                  readonly=True,
                                  states={'nhap': [('readonly', False)]})

    @api.constrains('bsd_sl_ky_tu')
    def _constrains_sl_kt(self):
        for each in self:
            if each.bsd_sl_ky_tu < 2:
                raise UserError(_("Độ dài chuỗi ký tự phải lớn hơn 2.\nvui lòng kiểm tra lại thông tin"))
    bsd_ma_tt_id = fields.Many2one('ir.sequence', string="Mã trình tự", help="Mã của trình tự", required=True)
    bsd_so_tt = fields.Integer(string='Số tiếp theo', help="Số tiếp theo được sử dụng",
                               compute='_compute_seq_number_next', inverse='_inverse_seq_number_next',
                               readonly=True,
                               states={'nhap': [('readonly', False)]})
    state = fields.Selection([('nhap', 'Nháp'),
                              ('active', 'Áp dụng'),
                              ('deactive', 'Ngưng sử dụng')],
                             string="Trạng thái", default='nhap', required=True, tracking=1, help="Trạng thái")

    @api.depends('bsd_ma_tt_id.number_next_actual')
    def _compute_seq_number_next(self):
        for each in self:
            if each.bsd_ma_tt_id:
                sequence = each.bsd_ma_tt_id._get_current_sequence()
                each.bsd_so_tt = sequence.number_next_actual
            else:
                each.bsd_so_tt = 1

    def _inverse_seq_number_next(self):
        for each in self:
            if each.bsd_ma_tt_id and each.bsd_so_tt:
                sequence = each.bsd_ma_tt_id._get_current_sequence()
                sequence.sudo().number_next = each.bsd_so_tt

    @api.model
    def _create_sequence(self, vals):
        prefix = vals['bsd_ma_cn']
        suffix = vals['bsd_ma_ht']
        seq = {
            'name': _('%s trình tự') % vals['bsd_ten_cn'],
            'implementation': 'no_gap',
            'prefix': prefix,
            'suffix': suffix,
            'padding': vals['bsd_sl_ky_tu'],
            'number_increment': 1,
        }
        seq = self.env['ir.sequence'].create(seq)
        return seq

    @api.model
    def create(self, vals):
        if 'bsd_du_an_id' in vals:
            du_an = self.env['bsd.du_an'].browse(vals['bsd_du_an_id'])
            if du_an.state != 'chuan_bi':
                raise UserError(_("Dự án đã phát hành. Vui lòng kiểm tra lại thông tin."))
        if not vals.get('bsd_ma_tt_id'):
            vals.update({'bsd_ma_tt_id': self.sudo()._create_sequence(vals).id})
        return super(BsdMaBoChungTu, self).create(vals)

    def write(self, vals):
        if 'bsd_ten_cn' in vals.keys():
            self.bsd_ma_tt_id.write({
                'name': _('%s trình tự') % vals['bsd_ten_cn'],
            })
        if 'bsd_ma_cn' in vals.keys():
            self.bsd_ma_tt_id.write({
                'prefix': vals['bsd_ma_cn'],
            })
        if 'bsd_ma_ht' in vals.keys():
            self.bsd_ma_tt_id.write({
                'suffix': vals['bsd_ma_ht'],
            })
        if 'bsd_sl_ky_tu' in vals.keys():
            self.bsd_ma_tt_id.write({
                'padding': vals['bsd_sl_ky_tu'],
            })
        return super(BsdMaBoChungTu, self).write(vals)