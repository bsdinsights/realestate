odoo.define('bsd_sale_chart.SaleChartRenderer', function(require){
'use strict';
    var Widget = require('web.Widget');
    var FieldManagerMixin = require('web.FieldManagerMixin');
    var relational_fields = require('web.relational_fields');
    var basic_fields = require('web.basic_fields');
    var core = require('web.core');
    var time = require('web.time');
    var session = require('web.session');
    var qweb = core.qweb;
    var _t = core._t;

    var SaleChartRenderer = Widget.extend(FieldManagerMixin, {
        template: 'bsd_sale_chart.data_filter',
        events: {
            'click #search' : '_onSearch',
            'click .bsd_header_toa': '_onCollapseToa',
            'click .bsd_header_tang': '_onCollapseTang',
            'keyup .create_tu_gia .o_td_field .o_input': '_onChangeTuGia',
            'keyup .create_den_gia .o_td_field .o_input': '_onChangeDenGia',
            'keyup .create_tu_dt .o_td_field .o_input': '_onChangeTuDt',
            'keyup .create_den_dt .o_td_field .o_input': '_onChangeDenDt',
            'change .create_unit .o_td_field': '_onChangeUnit',
            'change .create_view .o_td_field': '_onChangeView',
            'change .create_huong .o_td_field': '_onChangeHuong',
            'dblclick .bsd_unit': '_showUnit',
            'click .bsd_unit': '_clickTooltip',
            'click .tooltip .bsd_giu_cho': '_clickGiuCho',
            'click .tooltip .bsd_bao_gia': '_clickBaoGia',
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
            this.filter = {
                bsd_du_an_id: null,
                bsd_dot_mb_id: null,
                bsd_unit: null,
                bsd_view: null,
                bsd_huong: null,
                bsd_tu_gia: null,
                bsd_den_gia: null,
                bsd_tu_dt: null,
                bsd_den_dt: null,
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
                    bsd_dot_mb_id : new relational_fields.FieldMany2One(self,
                        'bsd_dot_mb_id',
                        self.model.get(recordID), {
                            mode: 'edit',
                            attrs: {
                                placeholder: _t('Chọn đợt mở bán'),
                                can_create: false,
                            }
                        }
                    ),
                    bsd_unit : new basic_fields.FieldChar(self,
                        'bsd_unit',
                        self.model.get(recordID), {
                            mode: 'edit',
                            attrs: {
                                placeholder: _t('Chọn căn hộ')
                            }
                        }
                    ),
                    bsd_view : new relational_fields.FieldSelection(self,
                        'bsd_view',
                        self.model.get(recordID), {
                            mode: 'edit',
                            attrs: {
                            }
                        }
                    ),
                    bsd_huong : new relational_fields.FieldSelection(self,
                        'bsd_huong',
                        self.model.get(recordID), {
                            mode: 'edit',
                            attrs: {
                            }
                        }
                    ),
                    bsd_tu_gia : new basic_fields.FieldFloat(self,
                        'bsd_tu_gia',
                        self.model.get(recordID), {
                            mode: 'edit',
                            attrs: {
                                placeholder: _t('Nhập giá từ')
                            },
                            currency: 1,
                        }
                    ),
                    bsd_den_gia : new basic_fields.FieldFloat(self,
                        'bsd_den_gia',
                        self.model.get(recordID), {
                            mode: 'edit',
                            attrs: {
                                placeholder: _t('Nhập giá đến')
                            }
                        }
                    ),
                    bsd_tu_dt : new basic_fields.FieldFloat(self,
                        'bsd_tu_dt',
                        self.model.get(recordID), {
                            mode: 'edit',
                            attrs: {
                                placeholder: _t('Nhập diện tích từ')
                            }
                        }
                    ),
                    bsd_den_dt : new basic_fields.FieldFloat(self,
                        'bsd_den_dt',
                        self.model.get(recordID), {
                            mode: 'edit',
                            attrs: {
                                placeholder: _t('Nhập diện tích đến')
                            }
                        }
                    )
                };
                self.fields.bsd_du_an_id.appendTo(self.$('.create_du_an_id .o_td_field'))
                self.fields.bsd_dot_mb_id.appendTo(self.$('.create_dot_mb_id .o_td_field'))

                self.fields.bsd_view.appendTo(self.$('.create_view .o_td_field'))
                self.fields.bsd_huong.appendTo(self.$('.create_huong .o_td_field'))
                self.fields.bsd_tu_gia.appendTo(self.$('.create_tu_gia .o_td_field'))
                self.fields.bsd_den_gia.appendTo(self.$('.create_den_gia .o_td_field'))
                self.fields.bsd_tu_dt.appendTo(self.$('.create_tu_dt .o_td_field'))
                self.fields.bsd_den_dt.appendTo(self.$('.create_den_dt .o_td_field'))
                self.fields.bsd_unit.appendTo(self.$('.create_unit .o_td_field'))

            });
            var def2 = this._super.apply(this, arguments);
            return Promise.all([def1, def2]);
        },

        /**
         * @private
         */
        _onSearch: function(event){
            var self = this
            var data_show = [];
            var $chart = self.$('#chart').empty();
            self._rpc({
                    model: 'bsd.sale_chart.widget',
                    method: 'action_search',
                    args: [self.filter],
                    context: self.context,
            }).then(function (data){
                var format_curency = ((money) => {
                        money = money.toString().replace(/(\d)(?=(\d{3})+(?!\d))/g, "$1.");
                        return money;
                });
                self.data= _.each(data, function(item,index,data){
                    if (item[7] === null){
                        item[7] = 0
                    }
                    if (item[8] !== null){
                        item[8] = format_curency(item[8])
                    }
                    if (item[10] === null){
                        item[10] = ''
                    }
                })
                var group_toa = _.groupBy(self.data, function(item) { return item[0]});
                _.each(group_toa, function(item,index,group_toa){
                    var toa = {};
                    toa.headerToa = [item[0][0],item[0][1]]
                    toa.state={
                            chuan_bi:0,
                            san_sang:0,
                            dat_cho:0,
                            giu_cho:0,
                            dat_coc:0,
                            chuyen_coc:0,
                            da_thu_coc:0,
                            hoan_tat_dat_coc:0,
                            thanh_toan_dot_1:0,
                            ky_thoa_thuan_coc:0,
                            du_dieu_kien:0,
                            da_ban:0,
                        }
                    var group_tang = _.groupBy(item, function(item){ return item[2]})
                    var k = [];
                    _.each(group_tang, function(item,index,group_tang){
                        var tang ={};
                        tang.headerTang=[item[0][2],item[0][3]]
                        tang.detailTang=item
                        tang.state={
                            chuan_bi:0,
                            san_sang:0,
                            dat_cho:0,
                            giu_cho:0,
                            dat_coc:0,
                            chuyen_coc:0,
                            da_thu_coc:0,
                            hoan_tat_dat_coc:0,
                            thanh_toan_dot_1:0,
                            ky_thoa_thuan_coc:0,
                            du_dieu_kien:0,
                            da_ban:0,
                        }
                        var countState =_.countBy(item,function(item){
                            if (item[6] == 'chuan_bi') {return 'chuan_bi'}
                            if (item[6] == 'san_sang') {return 'san_sang'}
                            if (item[6] == 'dat_cho') {return 'dat_cho'}
                            if (item[6] == 'giu_cho') {return 'giu_cho'}
                            if (item[6] == 'dat_coc') {return 'dat_coc'}
                            if (item[6] == 'chuyen_coc') {return 'chuyen_coc'}
                            if (item[6] == 'da_thu_coc') {return 'da_thu_coc'}
                            if (item[6] == 'hoan_tat_dat_coc') {return 'hoan_tat_dat_coc'}
                            if (item[6] == 'thanh_toan_dot_1') {return 'thanh_toan_dot_1'}
                            if (item[6] == 'ky_thoa_thuan_coc') {return 'ky_thoa_thuan_coc'}
                            if (item[6] == 'du_dieu_kien') {return 'du_dieu_kien'}
                            if (item[6] == 'da_ban') {return 'da_ban'}
                        })
                        if (countState){
                            Object.assign(tang.state, countState);
                            toa.state = Object.keys(toa.state).reduce(function(s,a) {
                                  s[a] = toa.state[a] + tang.state[a];
                                  return s;
                                }, {})
                        }
                        k.push(tang)
                    })
                    toa.detailToa= k
                    data_show.push(toa)

                });
                var $svg = $(qweb.render("bsd_sale_chart.chart", {'data': data_show}));
                $chart.append($svg)
            })
        },
        /**
         * @private
         */
        _onCollapseToa: function(event){
            var t =$(event.currentTarget).parent().find(".collapse")
            if (!t.hasClass("show")){
                $(event.currentTarget).find("i").removeClass("fa-plus-circle").addClass("fa-minus-circle")
            }
            else{
                $(event.currentTarget).find("i").removeClass("fa-minus-circle").addClass("fa-plus-circle")
            }
         },
        /**
         * @private
         */
        _onCollapseTang: function(event){
            var t =$(event.currentTarget).parent().find(".collapse")
            if (!t.hasClass("show")){
                $(event.currentTarget).find("i").removeClass("fa-chevron-circle-right").addClass("fa-chevron-circle-down")
            }
            else{
                $(event.currentTarget).find("i").removeClass("fa-chevron-circle-down").addClass("fa-chevron-circle-right")
            }
         },
        /**
         * @private hiển thị field tiền
         */
         _formatCurrency: function(money){
            money = money.toString().replace(/(\d)(?=(\d{3})+(?!\d))/g, "$1,");
            return money;
         },
        /**
         * @private giá từ thay đổi
         */
         _onChangeTuGia: function(event){
            event.stopPropagation();
            var temp = $(event.currentTarget).val()
            if (temp){
                this.filter.bsd_tu_gia =  Number(temp.replace(/[^0-9.-]+/g,""));
                $(event.currentTarget).val(this._formatCurrency(this.filter.bsd_tu_gia))
            }
            else {
                this.filter.bsd_tu_gia =  null
            }

         },
        /**
         * @private giá đến thay đổi
         */
         _onChangeDenGia: function(event){
            event.stopPropagation();
            var temp = $(event.currentTarget).val()
            if (temp){
                this.filter.bsd_den_gia =  Number(temp.replace(/[^0-9.-]+/g,""));
                $(event.currentTarget).val(this._formatCurrency(this.filter.bsd_den_gia))
            }
            else {
                this.filter.bsd_den_gia =  null
            }

         },
        /**
         * @private diện tích từ thay đổi
         */
         _onChangeTuDt: function(event){
            event.stopPropagation();
            var temp = $(event.currentTarget).val()
            if (temp){
                this.filter.bsd_tu_dt =  parseInt(temp)
            }
            else {
                this.filter.bsd_tu_dt =  null
            }

         },
        /**
         * @private Diện tích đến thay đổi
         */
         _onChangeDenDt: function(event){
            event.stopPropagation();
            var temp = $(event.currentTarget).val()
            if (temp){
                this.filter.bsd_den_dt =  parseInt(temp)
            }
            else {
                this.filter.bsd_den_dt =  null
            }
         },
        /**
         * @private Lấy giá trị khi thay đổi tên căn hộ
         */
         _onChangeUnit: function(event){
            event.stopPropagation();
            var temp = $(event.currentTarget).find('.o_input')[0].value
            if (temp){
                this.filter.bsd_unit =  temp
            }
            else {
                this.filter.bsd_unit =  null
            }

         },
        /**
         * @private Lấy giá trị khi thay đổi view căn hộ
         */
         _onChangeView: function(event){
            event.stopPropagation();
            var temp = $(event.currentTarget).find('.o_input')[0].value
            if (temp !== 'false'){
                this.filter.bsd_view =  temp
            }
            else {
                this.filter.bsd_view =  null
            }

         },
        /**
         * @private Lấy giá trị khi thay đổi hướng căn hộ
         */
         _onChangeHuong: function(event){
            event.stopPropagation();
            var temp = $(event.currentTarget).find('.o_input')[0].value
            if (temp !== 'false'){
                this.filter.bsd_huong =  temp
            }
            else {
                this.filter.bsd_huong =  null
            }
         },
        /**
         * Loads an action from the database given its ID.
         *
         * @todo: turn this in a service (DataManager)
         * @private
         * @param {integer|string} action's ID or xml ID
         * @param {Object} context
         * @returns {Promise<Object>} resolved with the description of the action
         */
        _loadAction: function (actionID, context) {
            var self = this;
            return new Promise(function (resolve, reject) {
                self.trigger_up('load_action', {
                    actionID: actionID,
                    context: context,
                    on_success: resolve,
                });
            });
        },
        /**
         * @private Show thông tin căn hộ
         */
         _showUnit: function(event){
            var self = this
            var unit_id = parseInt($(event.currentTarget).attr('id'))
            this._loadAction('bsd_sale_chart.bsd_product_template_gio_hang_action').then(function(action){
                action.res_id = unit_id
                action.flags={'mode': 'readonly'}
                self.do_action(action)

            })
//            this.do_action('bsd_sale_chart.bsd_product_template_gio_hang_action')
         },
        /**
         * @private Show tooltip
         */
         _clickTooltip: function(event){
            event.stopPropagation()
            var unit_id = parseInt($(event.currentTarget).attr('id'))
            var data_unit = _.find(this.data, function(item){return item[4] === unit_id})
            this._rpc({
                model: 'bsd.giu_cho',
                method: 'search_read',
                fields: ['bsd_ma_gc', 'bsd_khach_hang_id', 'bsd_stt_bg', 'bsd_ngay_hh_bg', 'state'],
                domain: [['state', 'in', ['dat_cho','giu_cho']], ['bsd_unit_id', '=', unit_id]]
            }).then(function(giu_cho){
                console.log("lấy thông tin giữ chỗ")
                console.log(giu_cho)
                var title = `<div>Diện tích sử dụng: ${data_unit[9]} m2</div>
                             <div>Loại căn hộ: ${data_unit[10]} </div>
                             <table class="table table-bordered table-sm">
                                <thead>
                                    <tr>
                                        <td>Mã giữ chỗ</td>
                                        <td>Khách hàng</td>
                                        <td>Số thứ tự </td>
                                    </tr>
                                </thead>
                             </table>`
                $(event.currentTarget).tooltip({
                template: `<div class="tooltip" role="tooltip">
                                <div class="arrow"></div>
                                <div class="tooltip-inner bsd_tooltip_title"></div>
                                <div class="bsd_tooltip_action" id=${data_unit[11]}>
                                    <span class="bsd_quan_tam">Quan tâm</span>
                                    <span class="bsd_giu_cho ml-4">Giữ chỗ</span>
                                    <span class="bsd_bao_gia ml-4">Bảng tính giá</span>
                                </div>
                            </div>
                           </div>`,
                title: title,
                delay: {show:0, hide:0},
                selector: '.bsd_title',
                placement: "top",
                trigger: "click focus",
                container: "#chart"
            }).tooltip("show")
            })


         },
        /**
         * @private tạo giữ chỗ
         */
         _clickGiuCho: function(event){
            event.stopPropagation()
            var self = this
            var unit_id = parseInt($(event.currentTarget).parent().attr('id'))
            this._loadAction('bsd_sale_chart.bsd_giu_cho_action').then(function(action){
                action.context={default_bsd_du_an_id:self.filter.bsd_du_an_id,
                                default_bsd_unit_id:unit_id}
                self.do_action(action)
            })
         },
        /**
         * @private tạo giữ chỗ
         */
         _clickBaoGia: function(event){
            event.stopPropagation()
            var self = this
            this.do_action({
                name: "Tạo báo giá",
                res_model: 'bsd.bao_gia',
                views: [[false, 'form']],
                type: 'ir.actions.act_window',
                view_mode: "form",
                target: "new"
            })
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
            else if (fieldName === 'bsd_dot_mb_id'){
                if (event.data.changes.bsd_dot_mb_id !== false){
                    var bsd_dot_mb_id = event.data.changes.bsd_dot_mb_id;
                    this.filter.bsd_dot_mb_id = bsd_dot_mb_id.id
                    this.trigger_up('change_dot_mb', {'data':bsd_dot_mb_id})
                }
                else {
                    var bsd_dot_mb_id = event.data.changes.bsd_dot_mb_id;
                    this.filter.bsd_dot_mb_id = null
                    this.trigger_up('change_dot_mb', {'data':bsd_dot_mb_id})
                }
            }
        },

        update: function(dataChange){
            var self = this;
            if (dataChange.field === 'bsd_dot_mb_id'){
                this._makeRecord(dataChange).then(function (recordID) {

                    self.fields.bsd_dot_mb_id.reset(self.model.get(recordID));
                });
            };
            if (dataChange.field === 'bsd_du_an_id'){
                this._makeRecord(dataChange).then(function (recordID) {
                    self.fields.bsd_du_an_id.reset(self.model.get(recordID));
                    self.fields.bsd_dot_mb_id.reset(self.model.get(recordID));
                });
            };
        },
    /**
     * @private
     * @returns {string} local id of the dataPoint
     */
        _makeRecord: function (data = null) {
            var self = this
            var field = [{
                    relation: 'bsd.du_an',
                    type: 'many2one',
                    name: 'bsd_du_an_id',
                },
                {
                    relation: 'bsd.dot_mb',
                    type: 'many2one',
                    name: 'bsd_dot_mb_id',
                    domain: [['bsd_du_an_id', '=', self.filter.bsd_du_an_id]]
                },
                {
                    type: 'char',
                    name: 'bsd_unit',
                },
                 {
                    type: 'selection',
                    name: 'bsd_view',
                    selection: [[1, 'Phố'],
                                 [2, 'Hồ bơi'],
                                 [3, 'Công viên'],
                                 [4, 'Mặt tiền'],
                                 [5, 'Bãi biển/sông/hồ/núi'],
                                 [6, 'Rừng'],
                                 [7, 'Cao tốc'],
                                 [8, 'Hồ'],
                                 [9, 'Biển']]
                },
                 {
                    type: 'selection',
                    name: 'bsd_huong',
                    selection:[[1, 'Đông'],
                                  [2, 'Tây'],
                                  [3, 'Nam'],
                                  [4, 'Bắc'],
                                  [5, 'Đông nam'],
                                  [6, 'Đông bắc'],
                                  [7, 'Tây nam'],
                                  [8, 'Tây bắc']]
                },
                {
                    type: 'float',
                    name: 'bsd_tu_gia',
                },
                {
                    type: 'float',
                    name: 'bsd_den_gia',
                },
                {
                    type: 'float',
                    name: 'bsd_tu_dt',
                },
                {
                    type: 'float',
                    name: 'bsd_den_dt',
                },
            ];
            if (data != null && data.data !== false){
                if (data.field === 'bsd_dot_mb_id'){
                    field[1].value = [data.data.id, data.data.display_name];
                }
                if (data.field === 'bsd_du_an_id'){
                    field[0].value = [data.data.id, data.data.display_name];
                    field[1].domain = [['bsd_du_an_id', '=', data.data.id]]
                }
            }
            return this.model.makeRecord('bsd.sale_chart.widget', field, {});

        },
    });
    return {
        SaleChartRenderer: SaleChartRenderer,
    };
})