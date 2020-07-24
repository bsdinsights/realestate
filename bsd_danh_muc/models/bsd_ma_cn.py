# -*- coding:utf-8 -*-

from odoo import models, fields, api, _


class BsdMaBoChungTu(models.Model):
    _name = 'bsd.ma_bo_cn'
    _description = "Cách đánh mã bộ chứng từ"
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _rec_name = 'bsd_ten_cn'

    bsd_ten_cn = fields.Char(string="Tên", help="Tên bộ chứng từ", required=True)
    bsd_du_an_id = fields.Many2one('bsd.du_an', string="Dự án", help="Dự án")
    bsd_loai_cn = fields.Selection([('bsd.du_an', 'Dự án'),
                                    ('bsd.gc_tc', 'Giữ chỗ thiện chí'),
                                    ('bsd.rap_can', 'Ráp căn'),
                                    ('bsd.giu_cho', 'Giữ chỗ'),
                                    ('bsd.bao_gia', 'Bảng tính giá'),
                                    ('bsd.dat_coc', 'Đặt cọc'),
                                    ('bsd.hd_ban', 'Hợp đồng'),
                                    ('bsd.phieu_thu', 'Phiếu thu'),
                                    ('bsd.hoan_tien', 'Hoàn tiền'),
                                    ('bsd.giam_no', 'Điều chỉnh giảm'),
                                    ('bsd.tang_no', 'Điều chỉnh tăng'),
                                    ('bsd.chuyen_tien', 'Chuyển tiền'),
                                    ('bsd.huy_gc', 'Hủy giữ chỗ'),
                                    ('bsd.dot_mb', 'Mã đợt mở bán'),
                                    ('bsd.them_unit', 'Mã thêm căn hộ vào đợt mở bán'),
                                    ('bsd.thu_hoi', 'Mã thu hồi căn hộ'),
                                    ('bsd.kh_cn', 'Khách hàng cá nhân'),
                                    ('bsd.kh_dn', 'Khách hàng doanh nghiệp'),
                                    ('bsd.chiet_khau', 'Chiết khấu'),
                                    ('bsd.ck_ch', 'Chiết khấu chung'),
                                    ('bsd.ck_ms', 'Chiết khấu mua sỉ'),
                                    ('bsd.ck_nb', 'Chiết khấu nội bộ'),
                                    ('bsd.ck_ttn', 'Chiết khấu thanh toán nhanh'),
                                    ('bsd.ck_cstt', 'Chiết khấu theo chính sách thanh toán'),
                                    ('bsd.ck_ttth', 'Chiết khấu thanh toán trước hạn'),
                                    ('bsd.ck_db', 'Chiết khấu đặc biệt'),
                                    ('bsd.ps_gd_ck', 'Giao dịch chiết khấu'),
                                    ('bsd.khuyen_mai', 'Chương trình khuyến mãi'),
                                    ('bsd.ps_gd_km', 'Giao dịch khuyến mãi'),
                                    ('bsd.chuyen_gc', 'Chuyển tên khách hàng giữ chỗ'),
                                    ('bsd.hd_ban_cn', 'Chuyển nhượng hợp đồng'),
                                    ('bsd.cn_dkbg', 'Cập nhật dự kiến bàn giao'),
                                    ('bsd.cn_dkbg_unit', 'Cập nhật dự kiến bàn giao chi tiết'),
                                    ('bsd.ds_tb', 'Danh sách thông báo'),
                                    ('bsd.tb_nt', 'Thông báo nghiệm thu'),
                                    ('bsd.nghiem_thu', 'Nghiệm thu')],
                                   string="Loại chứng từ", help="Loại chứng từ được đặt mã", required=True)
    bsd_ma_cn = fields.Char(string="Mã chứng từ", help="Mã tiền tố của chứng từ", required=True)
    _sql_constraints = [
        ('bsd_ma_cn_unique', 'unique (bsd_ma_cn)',
         'Mã tiền tố chứng từ đã tồn tại !'),
    ]
    bsd_sl_ky_tu = fields.Integer(string="Độ dài chuỗi", help="Độ dài chuổi ký tự sinh tự động của hệ thống",
                                  required=True)
    bsd_ma_tt_id = fields.Many2one('ir.sequence', string="Mã trình tự", help="Mã của trình tự", required=True)
    bsd_so_tt = fields.Integer(string='Số tiếp theo', help="Số tiếp theo được sử dụng",
                               compute='_compute_seq_number_next', inverse='_inverse_seq_number_next')
    state = fields.Selection([('active', 'Đang sử dụng'),
                              ('inactive', 'Không sử dụng')],
                             string="Trạng thái", default='active', required=True, tracking=1, help="Trạng thái")

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
    def _create_sequence(self, vals,):
        prefix = vals['bsd_ma_cn']
        seq = {
            'name': _('%s trình tự') % vals['bsd_ten_cn'],
            'implementation': 'no_gap',
            'prefix': prefix,
            'padding': vals['bsd_sl_ky_tu'],
            'number_increment': 1,
        }
        seq = self.env['ir.sequence'].create(seq)
        return seq

    @api.model
    def create(self, vals):
        if not vals.get('bsd_ma_tt_id'):
            vals.update({'bsd_ma_tt_id': self.sudo()._create_sequence(vals).id})
        return super(BsdMaBoChungTu, self).create(vals)