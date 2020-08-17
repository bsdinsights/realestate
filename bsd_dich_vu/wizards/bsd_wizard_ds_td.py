from odoo import fields, models, api


class BsdWizardKTXN(models.TransientModel):
    _name = 'bsd.wizard.ds_td.kt_xn'
    _description = 'Kế toán xác nhận công nợ'

    def _get_ds_td(self):
        return self.env['bsd.ds_td'].browse(self._context.get('active_ids', []))
    bsd_ds_td_id = fields.Many2one('bsd.ds_td', string="Danh sách theo dõi", default=_get_ds_td, readonly=True)
    bsd_thong_bao = fields.Char(default="Bạn có muốn xác nhận yêu cầu này không", readonly=True)

    def action_co(self):
        self.bsd_ds_td_id.write({
            'state': 'hoan_thanh'
        })

    def action_khong(self):
        self.bsd_ds_td_id.write({
            'state': 'nhap',
            'bsd_ly_do': 'Công nợ chưa đúng'
        })


class BsdHuyDSTD(models.Model):
    _name = 'bsd.wizard.ds_td.huy'
    _description = 'Hủy danh sách theo dõi'

    def _get_ds_td(self):
        return self.env['bsd.ds_td'].browse(self._context.get('active_ids', []))
    bsd_ds_td_id = fields.Many2one('bsd.ds_td', string="Danh sách theo dõi", default=_get_ds_td, readonly=True)
    bsd_ly_do = fields.Char(default="Lý do", readonly=True)

    def action_xac_nhan(self):
        if self.bsd_ds_td_id.state in ['nhap', 'xac_nhan']:
            self.bsd_ds_td_id.write({
                'state': 'huy',
                'bsd_ly_do': self.bsd_ly_do
            })