# -*- conding:utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError
import logging
import datetime
_logger = logging.getLogger(__name__)


class BsdGiaHanGiuCho(models.Model):
    _name = 'bsd.gia_han_gc'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _rec_name = 'bsd_ma'
    _description = 'Phiếu gia hạn giữ chỗ'

    bsd_ma = fields.Char(string="Mã", help="Mã phiếu gia hạn giữ chỗ", required=True, readonly=True, copy=False,
                         default='/')
    _sql_constraints = [
        ('bsd_ma_unique', 'unique (bsd_ma)',
         'Mã phiếu gia hạn đã tồn tại !')]
    bsd_ngay = fields.Date(string="Ngày", help="Ngày gia hạn giữ chỗ", default=lambda self: fields.Date.today(),
                                  readonly=True, required=True,
                                  states={'nhap': [('readonly', False)]})
    bsd_tieu_de = fields.Char(string="Tiêu đề", help="Tiêu đề phiếu gia hạn giữ chỗ", required=True,
                              readonly=True,
                              states={'nhap': [('readonly', False)]})

    @api.model
    def default_get(self, fields_list):
        res = super(BsdGiaHanGiuCho, self).default_get(fields_list)
        if self._context.get('active_model') == 'bsd.giu_cho':
            giu_cho = self.env['bsd.giu_cho'].browse(self._context.get('active_ids', []))
            if giu_cho:
                du_an = giu_cho.mapped('bsd_du_an_id')
                if len(du_an) > 1:
                    raise UserError(_("Chọn giữ chỗ nằm ở 2 dự án khác nhau.\nVui lòng kiểm tra lại."))
                item = []
                for gc in giu_cho:
                    item.append((0, 0, {'bsd_giu_cho_id': gc.id,
                                        'bsd_han_ht': gc.bsd_ngay_hh_gc,
                                        'state': 'cho_duyet'}))
                res.update({
                    'bsd_du_an_id': du_an.id,
                    'bsd_tieu_de': "Gia hạn giữ chỗ",
                    'bsd_ct_ids': item
                })
        else:
            gc_tc = self.env['bsd.gc_tc'].browse(self._context.get('active_ids', []))
            if gc_tc:
                du_an = gc_tc.mapped('bsd_du_an_id')
                if len(du_an) > 1:
                    raise UserError(_("Chọn giữ chỗ nằm ở 2 dự án khác nhau.\nVui lòng kiểm tra lại."))
                item = []
                for gc in gc_tc:
                    item.append((0, 0, {'bsd_gc_tc_id': gc.id,
                                        'bsd_han_ht': gc.bsd_ngay_hh_gctc,
                                        'state': 'cho_duyet'}))
                res.update({
                    'bsd_du_an_id': du_an.id,
                    'bsd_tieu_de': "Gia hạn giữ chỗ thiện chí",
                    'bsd_gctc_ct_ids': item
                })
        return res
    bsd_du_an_id = fields.Many2one("bsd.du_an", string="Dự án", help="Dự án", required=True,
                                   readonly=True,
                                   states={'nhap': [('readonly', False)]})
    bsd_loai_gc = fields.Selection([('gc_tc', 'Giữ chỗ thiện chí'),
                                    ('giu_cho', 'Giữ chỗ')], string="Loại giữ chỗ", required=True,
                                   readonly=True,
                                   states={'nhap': [('readonly', False)]})
    bsd_loai_gh = fields.Selection([('san_pham', 'Sản phẩm'),
                                    ('hang_loat', 'Hàng loạt')], string="Loại gia hạn",
                                   readonly=True, required=True, default='hang_loat',
                                   states={'nhap': [('readonly', False)]})
    bsd_so_ngay = fields.Integer(string="Số ngày gia hạn", help="Số ngày gia hạn cho giữ chỗ",
                                 readonly=True,
                                 states={'nhap': [('readonly', False)]})
    state = fields.Selection([('nhap', 'Nháp'), ('xac_nhan', 'Xác nhận'),
                              ('da_duyet', 'Duyệt'), ('huy', 'Hủy')], string="Trạng thái", help="Trạng thái",
                             required=True, default='nhap', tracking=1)
    bsd_ct_ids = fields.One2many('bsd.gia_han_gc_ct', 'bsd_gia_han_id', string="Giữ chỗ",
                                 readonly=True,
                                 states={'nhap': [('readonly', False)]})
    bsd_gctc_ct_ids = fields.One2many('bsd.gia_han_gctc_ct', 'bsd_gia_han_id', string="Giữ chỗ thiện chí",
                                      readonly=True,
                                      states={'nhap': [('readonly', False)]})
    bsd_dien_giai = fields.Char(string="Diễn giải",
                                readonly=True,
                                states={'nhap': [('readonly', False)]})
    bsd_ngay_duyet = fields.Datetime(string="Ngày duyệt", readonly=True)
    bsd_nguoi_duyet_id = fields.Many2one('res.users', string="Người duyệt", readonly=True)

    @api.onchange('bsd_so_ngay', 'bsd_loai_gh', 'bsd_loai_gc')
    def _onchange_so_ngay(self):
        if self.bsd_loai_gh == 'hang_loat':
            if self.bsd_loai_gc == 'gc_tc':
                for ct in self.bsd_gctc_ct_ids:
                    ct.bsd_ngay_gh = ct.bsd_han_ht + datetime.timedelta(days=self.bsd_so_ngay)
                    _logger.debug(ct.bsd_ngay_gh)
            elif self.bsd_loai_gc == 'giu_cho':
                for ct in self.bsd_ct_ids:
                    ct.bsd_ngay_gh = ct.bsd_han_ht + datetime.timedelta(days=self.bsd_so_ngay)

    def action_xac_nhan(self):
        if self.state == 'nhap':
            self.write({
                'state': 'xac_nhan',
            })

    def action_xac_nhan_popup(self):
        if self.state == 'nhap':
            self.write({
                'state': 'xac_nhan',
            })
        return {
            'type': 'ir.actions.act_window',
            'name': 'Gia hạn giữ chỗ',
            'res_model': 'bsd.gia_han_gc',
            'res_id': self.id,
            'target': 'current',
            'view_mode': 'form'
        }

    def action_duyet(self):
        if self.state == 'xac_nhan':
            self.write({
                'state': 'da_duyet',
                'bsd_ngay_duyet': fields.Datetime.now(),
                'bsd_nguoi_duyet_id': self.env.uid,
            })
            if self.bsd_loai_gc == 'giu_cho':
                for ct in self.bsd_ct_ids:
                    if ct.bsd_giu_cho_id.state in ['dang_cho', 'giu_cho']:
                        ct.write({
                            'state': 'hieu_luc',
                        })
                        ct.bsd_giu_cho_id.write({
                            'bsd_ngay_hh_gc': ct.bsd_ngay_gh
                        })
                    else:
                        ct.write({
                            'bsd_ly_do': 'Giữ chỗ đã hết hiệu lực',
                        })
            else:
                for ct in self.bsd_gctc_ct_ids:
                    if ct.bsd_gc_tc_id.state in ['cho_rc', 'giu_cho']:
                        ct.write({
                            'state': 'hieu_luc',
                        })
                        ct.bsd_gc_tc_id.write({
                            'bsd_ngay_hh_gctc': ct.bsd_ngay_gh
                        })
                    else:
                        ct.write({
                            'bsd_ly_do': 'Giữ chỗ đã hết hiệu lực',
                        })

    # KD.05.07.04 Hủy chuyển tên khách hàng giữ chỗ
    def action_huy(self):
        if self.state in ['xac_nhan', 'nhap']:
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
            raise UserError(_('Dự án chưa có mã phiếu gia hạn giữ chỗ.'))
        vals['bsd_ma'] = sequence.next_by_id()
        res = super(BsdGiaHanGiuCho, self).create(vals)
        if res.bsd_loai_gh == 'hang_loat':
            if res.bsd_loai_gc == 'giu_cho':
                self.env.cr.execute("""
                    SELECT id FROM bsd_giu_cho 
                        WHERE bsd_du_an_id = {0} AND state IN ('dang_cho','giu_cho')
                """.format(res.bsd_du_an_id.id))
                gc_ids = self.env['bsd.giu_cho'].browse([item[0] for item in self.env.cr.fetchall()])
                list_ct = []
                for gc in gc_ids:
                    list_ct.append((0, 0, {'bsd_giu_cho_id': gc.id,
                                           'bsd_han_ht': gc.bsd_ngay_hh_gc,
                                           'bsd_ngay_gh': gc.bsd_ngay_hh_gc + datetime.timedelta(
                                               days=res.bsd_so_ngay),
                                           'state': 'cho_duyet'}))
                res.write({
                    'bsd_ct_ids': list_ct
                })
            else:
                self.env.cr.execute("""
                    SELECT id FROM bsd_gc_tc 
                        WHERE bsd_du_an_id = {0} AND state IN ('cho_rc','giu_cho')
                """.format(res.bsd_du_an_id.id))
                gc_tc_ids = self.env['bsd.gc_tc'].browse([item[0] for item in self.env.cr.fetchall()])
                list_ct = []
                for gc in gc_tc_ids:
                    list_ct.append((0, 0, {'bsd_gc_tc_id': gc.id,
                                           'bsd_han_ht': gc.bsd_ngay_hh_gctc,
                                           'bsd_ngay_gh': gc.bsd_ngay_hh_gctc + datetime.timedelta(
                                                days=res.bsd_so_ngay),
                                           'state': 'cho_duyet'}))
                res.write({
                    'bsd_gctc_ct_ids': list_ct
                })
        return res


class BsdGiaHanGiuChoChiTiet(models.Model):
    _name = 'bsd.gia_han_gc_ct'
    _description = 'Chi tiết các giữ chỗ được gia hạn'

    bsd_gia_han_id = fields.Many2one('bsd.gia_han_gc', string="Gia hạn GC", help="Gia hạn giữ chỗ", required=True)
    bsd_ngay_gh = fields.Datetime(string="Ngày gia hạn", help="Ngày gia hạn của giữ chỗ")
    bsd_ly_do = fields.Char(string="Lý do", help="Lý do giữ chỗ không được gia hạn", readonly=True)
    bsd_giu_cho_id = fields.Many2one('bsd.giu_cho', string="Giữ chỗ", help="Giữ chỗ")
    bsd_han_ht = fields.Datetime(string="Hạn giữ chỗ", help="Hạn giữ chỗ hiện tại", readonly=True)
    state = fields.Selection([('cho_duyet', 'Chờ duyệt'),
                              ('hieu_luc', 'Hiệu lực'),
                              ('huy', 'Hủy')], string="Trạng thái",
                             readony=True, required=True, default='cho_duyet')


class BsdGiaHanGiuChoThienChiChiTiet(models.Model):
    _name = 'bsd.gia_han_gctc_ct'
    _description = 'Chi tiết các giữ chỗ thiện chí được gia hạn'

    bsd_gia_han_id = fields.Many2one('bsd.gia_han_gc', string="Gia hạn GC", help="Gia hạn giữ chỗ", required=True)
    bsd_ngay_gh = fields.Datetime(string="Ngày gia hạn", help="Ngày gia hạn của giữ chỗ")
    bsd_ly_do = fields.Char(string="Lý do", help="Lý do giữ chỗ không được gia hạn", readonly=True)
    bsd_gc_tc_id = fields.Many2one('bsd.gc_tc', string="Giữ chỗ thiện chí", help="Giữ chỗ thiện chí", required=True)
    bsd_han_ht = fields.Datetime(string="Hạn giữ chỗ", help="Hạn giữ chỗ hiện tại", readonly=True)
    state = fields.Selection([('cho_duyet', 'Chờ duyệt'),
                              ('hieu_luc', 'Hiệu lực'),
                              ('huy', 'Hủy')], string="Trạng thái",
                             required=True, readony=True,
                             default='cho_duyet')