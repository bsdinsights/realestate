odoo.define('bsd_bao_cao.SaleChartRenderer', function(require){
'use strict';
    var Widget = require('web.Widget');
    var FieldManagerMixin = require('web.FieldManagerMixin');
    var relational_fields = require('web.relational_fields');
    var basic_fields = require('web.basic_fields');
    var BasicModel = require('web.BasicModel');
    var core = require('web.core');
    var time = require('web.time');
    var session = require('web.session');
    var qweb = core.qweb;
    var _t = core._t;

    var SaleChartRenderer = Widget.extend(FieldManagerMixin, {
        template: 'bsd_bao_cao.data_filter',
        events: {
            'click #search' : '_onSearch',
            'click #excel' : '_onExportExcel',
            'change .create_loai .o_td_field': '_onChangeLoai',
            'keyup .create_tu_ngay .o_td_field': '_onChangeTuNgay',
            'keyup .create_den_ngay .o_td_field': '_onChangeDenNgay',
        },
        custom_events: _.extend({}, FieldManagerMixin.custom_events,{
            'field_changed': '_onFieldChange',
        }),
        /**
         * @override
         */
         init: function(parent, model, state){
            this._super(parent);
            this.model = model;
            this._initialState = state;
            this.data = [],
            this.interval = null
            this.filter = {
                bsd_du_an_id: null,
                bsd_loai: null,
                bsd_tu_ngay: null,
                bsd_den_ngay: null,
            };
         },
        /**
         * @override
         */
        start: function () {
            var self = this;
            var def1 = this._makeRecord().then(function (recordID) {
                self.fields = {
                    bsd_du_an_id : new relational_fields.FieldMany2One(self,
                        'bsd_du_an_id',
                        self.model.get(recordID), {
                            mode: 'edit',
                            attrs: {
                                placeholder: _t('Chọn dự án'),
                                can_create: false,
                            }
                        }
                    ),
                    bsd_loai : new relational_fields.FieldSelection(self,
                        'bsd_loai',
                        self.model.get(recordID), {
                            mode: 'edit',
                            attrs: {
                                placeholder: _t('Loại báo cáo')
                            }
                        }
                    ),
                    bsd_tu_ngay : new basic_fields.FieldDate(self,
                        'bsd_tu_ngay',
                        self.model.get(recordID), {
                            mode: 'edit',
                            attrs: {
                                placeholder: _t('Nhập từ ngày')
                            },
                        }
                    ),
                    bsd_den_ngay : new basic_fields.FieldDate(self,
                        'bsd_den_ngay',
                        self.model.get(recordID), {
                            mode: 'edit',
                            attrs: {
                                placeholder: _t('Nhập từ ngày')
                            },
                        }
                    )
                };
                self.fields.bsd_du_an_id.appendTo(self.$('.create_du_an_id .o_td_field'))
                self.fields.bsd_loai.appendTo(self.$('.create_loai .o_td_field'))
                self.fields.bsd_tu_ngay.appendTo(self.$('.create_tu_ngay .o_td_field'))
                self.fields.bsd_den_ngay.appendTo(self.$('.create_den_ngay .o_td_field'))
            });
            var def2 = this._super.apply(this, arguments);
            return Promise.all([def1, def2]);
        },
        /**
         * Destroys the current widget, also destroys all its children before
         * destroying itself.
         */
        destroy: function () {
            var self = this
            clearInterval(self.interval);
            this._super();

        },

        /**
         * @private hiện thị báo cáo
         */
        _onSearch: function(event){
            var self = this
            var $chart = self.$('#chart').empty();
            self._rpc({
                    model: 'bsd.bao_cao.widget',
                    method: 'action_search',
                    args: [self.filter],
                    context: self.context,
            }).then(function (data){
                var format_number = ((x) => {
                    var parts = x.toString().split(".");
                    parts[0] = parts[0].replace(/\B(?=(\d{3})+(?!\d))/g, ".");
                    return parts.join(",");
                    })
                _.each(data, function(item, index, data){
                    if (item[3] == 'chuan_bi'){
                        item[3] = 'Chuẩn bị'
                    }
                    else if (item[3] == 'san_sang'){
                        item[3] = 'Sẵn sàng'
                    }
                    else if (item[3] == 'dat_cho'){
                        item[3] = 'Đặt chỗ'
                    }
                    else if (item[3] == 'giu_cho'){
                        item[3] = 'Giữ chỗ'
                    }
                    else if (item[3] == 'dat_coc'){
                        item[3] = 'Đặt cọc'
                    }
                    else if (item[3] == 'chuyen_coc'){
                        item[3] = 'Chuyển cọc'
                    }
                    else if (item[3] == 'da_tc'){
                        item[3] = 'Đã thu cọc'
                    }
                    else if (item[3] == 'ht_dc'){
                        item[3] = 'Hoàn tất đặt cọc'
                    }
                    else if (item[3] == 'tt_dot_1'){
                        item[3] = 'Thanh toán đợt 1'
                    }
                    else if (item[3] == 'ky_tt_coc'){
                        item[3] = 'Ký thỏa thuận cọc'
                    }
                    else if (item[3] == 'du_dk'){
                        item[3] = 'Đủ điều kiện'
                    }
                    else if (item[3] == 'da_ban'){
                        item[3] = 'Đã bán'
                    }
                    _.each(item[6], function(item_b,index_b,data_n){
                        console.log(item_b[3])
                        item_b[1] = format_number(item_b[1])
                        if (item_b[3] !== null){
                            let time = new moment.utc(item_b[3])
                            item_b[3] = time.local().format('DD/MM/YYYY')
                        }
                    })
                })
                $chart.append($(qweb.render("bsd_bao_cao.dot_tt", {'data': data})))
            })

        },
         /**
         * @private xuất dữ liệu excel
         */
        _onExportExcel: function(event){
            var self = this
            self._rpc({
                    model: 'bsd.bao_cao.widget',
                    method: 'action_export_xlsx',
                    args: [self.filter],
                    context: self.context,
            }).then(function (data){
            })

        },
        /**
         * @private Lấy giá trị khi thay đổi loại báo cáo
         */
         _onChangeLoai: function(event){
            event.stopPropagation();
            let temp = $(event.currentTarget).find('.o_input')[0].value
            if (temp !== 'false'){
                this.filter.bsd_loai =  temp.replaceAll('"','')
            }
            else {
                this.filter.bsd_loai =  null
            }
         },

        /**
         * @private Lấy giá trị khi thay đổi từ ngày
         */
         _onChangeTuNgay: function(event){
            event.stopPropagation();
            var temp = $(event.currentTarget).find('.o_input')[0].value
            if (temp !== 'false'){
                this.filter.bsd_tu_ngay =  temp
            }
            else {
                this.filter.bsd_tu_ngay =  null
            }
         },
        /**
         * @private Lấy giá trị khi thay đổi đến ngày
         */
         _onChangeDenNgay: function(event){
            event.stopPropagation();
            var temp = $(event.currentTarget).find('.o_input')[0].value
            if (temp !== 'false'){
                this.filter.bsd_den_ngay =  temp
            }
            else {
                this.filter.bsd_den_ngay =  null
            }
         },
        /**
         * @private Thay đổi dự án đợt mở bán
         */
        _onFieldChange: function(event){
            event.stopPropagation();
            var fieldName = event.target.name;
            if (fieldName === 'bsd_du_an_id'){
                if (event.data.changes.bsd_du_an_id !== false){
                    var bsd_du_an_id = event.data.changes.bsd_du_an_id;
                    this.filter.bsd_du_an_id = bsd_du_an_id.id
                    this.trigger_up('change_du_an', {'data':bsd_du_an_id})
                }
                else {
                    var bsd_du_an_id = event.data.changes.bsd_du_an_id;
                    this.filter.bsd_du_an_id = null
                    this.trigger_up('change_du_an', {'data':bsd_du_an_id})
                }
            }
        },
        update: function(dataChange){
            var self = this;
            if (dataChange.field === 'bsd_du_an_id'){
                this._makeRecord(dataChange).then(function (recordID) {
                    self.fields.bsd_du_an_id.reset(self.model.get(recordID));
                });
            };
        },
    /**
     * @private
     * @returns {string} local id of the dataPoint
     */
        _makeRecord: function (data = null) {
            console.log("tao record")
            console.log(data)
            var self = this
            var field = [{
                    relation: 'bsd.du_an',
                    type: 'many2one',
                    name: 'bsd_du_an_id',
                    domain: [['state', '=', 'phat_hanh']]
                },
                {
                    type: 'selection',
                    name: 'bsd_loai',
                    selection:[
                        ['tl_hd', 'Thanh lý hợp đồng'],
                        ['dot_tt', 'Đợt thanh toán']]
                },
                {
                    type: 'date',
                    name: 'bsd_tu_ngay',
                },
                {
                    type: 'date',
                    name: 'bsd_den_ngay',
                },
            ];
            if (data != null && data.data != null){
                if (data.field === 'bsd_du_an_id'){
                    field[0].value = [data.data.id, data.data.display_name];
                    field[1].domain = [['bsd_du_an_id', '=', data.data.id]]
                }
            }
            return this.model.makeRecord('bsd.bao_cao.widget', field, {});
        },
    });
    return {
        SaleChartRenderer: SaleChartRenderer,
    };
})