odoo.define('bsd_sale_chart.SaleChartRenderer', function(require){
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
            'click .tooltip .bsd_quan_tam': '_clickQuanTam',
            'click .mo_giu_cho': '_clickMoGiuCho',
            'scroll': '_scrollUnit',
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
                bsd_dot_mb_id: null,
                bsd_unit: null,
                bsd_view_ids: [],
                bsd_state: [],
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
                                can_write: false,
                                string: "Dự án",
                            },
//                            noOpen: true,
                            additionalContext: {'form_view_ref': 'bsd_du_an.bsd_du_an_form_popup'},
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
                                placeholder: _t('Chọn căn hộ'),
                            }
                        }
                    ),
                    bsd_view_ids : new relational_fields.FieldMany2ManyTags(self,
                        'bsd_view_ids',
                        self.model.get(recordID), {
                            mode: 'edit',
                            attrs: {
                                placeholder: _t('Chọn hướng nhìn'),
                                string: "Hướng nhìn",
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
                    bsd_tu_gia : new basic_fields.FieldChar(self,
                        'bsd_tu_gia',
                        self.model.get(recordID), {
                            mode: 'edit',
                            attrs: {
                                placeholder: _t('Nhập giá từ')
                            },
                            currency: 1,
                        }
                    ),
                    bsd_den_gia : new basic_fields.FieldChar(self,
                        'bsd_den_gia',
                        self.model.get(recordID), {
                            mode: 'edit',
                            attrs: {
                                placeholder: _t('Nhập giá đến')
                            }
                        }
                    ),
                    bsd_tu_dt : new basic_fields.FieldChar(self,
                        'bsd_tu_dt',
                        self.model.get(recordID), {
                            mode: 'edit',
                            attrs: {
                                placeholder: _t('Nhập diện tích từ')
                            }
                        }
                    ),
                    bsd_den_dt : new basic_fields.FieldChar(self,
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
                self.fields.bsd_huong.appendTo(self.$('.create_huong .o_td_field'))
                self.fields.bsd_tu_gia.appendTo(self.$('.create_tu_gia .o_td_field'))
                self.fields.bsd_den_gia.appendTo(self.$('.create_den_gia .o_td_field'))
                self.fields.bsd_tu_dt.appendTo(self.$('.create_tu_dt .o_td_field'))
                self.fields.bsd_den_dt.appendTo(self.$('.create_den_dt .o_td_field'))
                self.fields.bsd_unit.appendTo(self.$('.create_unit .o_td_field'))
                self.fields.bsd_view_ids.appendTo(self.$('.create_view_ids .o_td_field'))
                self.$("#select_state").bsMultiSelect({
                      placeholder: 'Chọn trạng thái',
                      cssPatch : {choices: {columnCount:'2' }}
                })
            });
            var def2 = this._super.apply(this, arguments);
            return Promise.all([def1, def2]);
        },
        updateUnit: function(){
            var self = this
            var id_unit = []
            var $unit_ids = $('.bsd_unit')
            if ($unit_ids.length){
                _.each($unit_ids,function(item,index,data){
                    if ($(item).inView()){
                        id_unit.push(parseInt($(item).attr("id")))
                    }
                })
                this._rpc({
                    model: 'bsd.sale_chart.widget',
                    method: 'action_update_unit',
                    args: [id_unit],
                    context: self.context,
                },{shadow : true}).then(function(data){
                    if (data !== undefined){
                    _.each(data,function(item,index,data){
                        if (item[0] != null){
                            var id = '#' + item[0].toString()
                            if ($(id).attr('class')){
                                var state = $(id).attr('class').replace("bsd_unit", "")
                                if (item[2] === null) {
                                    item[2] = 0
                                }
                                $(id).removeClass(state).addClass(item[1])
                                $(id).find(".so_giu_cho").text(item[2].toString())
                                $(id).find(".so_quan_tam").text(item[3].toString())
                            }

                        }
                    })
                    }
                })
            }
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
         * @private
         */
        _onSearch: function(event){
            var self = this
            var data_show = [];
            var $chart = self.$('#chart').empty();
            self.filter.bsd_state = self.$('#select_state').val()
            self._rpc({
                    model: 'bsd.sale_chart.widget',
                    method: 'action_search',
                    args: [self.filter],
                    context: self.context,
            }).then(function (data){
                var format_number = ((x) => {
                    var parts = x.toString().split(".");
                    parts[0] = parts[0].replace(/\B(?=(\d{3})+(?!\d))/g, ".");
                    return parts.join(",");
                });
                self.data= _.each(data, function(item,index,data){
                    if (item[7] === null){
                        item[7] = 0
                    }
                    if (item[8] !== null){
                        item[8] = format_number(item[8])
                    }
                    if (item[9] !== null){
                        item[9] = format_number(item[9])
                    }
                    if (item[10] === null){
                        item[10] = ''
                    }
                })
                var group_toa = _.groupBy(self.data, function(item) { return item[0]});
                _.each(group_toa, function(item,index,group_toa){
                    var toa = {};
                    toa.headerToa = [item[0][0],item[0][1]]
                    toa.sl = 0
                    toa.state={
                            chuan_bi:0,
                            san_sang:0,
                            dat_cho:0,
                            giu_cho:0,
                            dat_coc:0,
                            chuyen_coc:0,
                            da_tc:0,
                            ht_dc:0,
                            tt_dot_1:0,
                            ky_tt_coc:0,
                            du_dk:0,
                            da_ban:0,
                        }
                    var group_tang = _.groupBy(item, function(item){ return item[14]})
                    var k = [];;
                    _.each(group_tang, function(item,index,group_tang){
                        var tang ={};
                        tang.headerTang=[item[0][2],item[0][3]]
                        tang.detailTang=item
                        tang.sl = item.length
                        toa.sl += tang.sl
                        tang.state={
                            chuan_bi:0,
                            san_sang:0,
                            dat_cho:0,
                            giu_cho:0,
                            dat_coc:0,
                            chuyen_coc:0,
                            da_tc:0,
                            ht_dc:0,
                            tt_dot_1:0,
                            ky_tt_coc:0,
                            du_dk:0,
                            da_ban:0,
                        }
                        var countState =_.countBy(item,function(item){
                            if (item[6] == 'chuan_bi') {return 'chuan_bi'}
                            if (item[6] == 'san_sang') {return 'san_sang'}
                            if (item[6] == 'dat_cho') {return 'dat_cho'}
                            if (item[6] == 'giu_cho') {return 'giu_cho'}
                            if (item[6] == 'dat_coc') {return 'dat_coc'}
                            if (item[6] == 'chuyen_coc') {return 'chuyen_coc'}
                            if (item[6] == 'da_tc') {return 'da_tc'}
                            if (item[6] == 'ht_dc') {return 'ht_dc'}
                            if (item[6] == 'tt_dot_1') {return 'tt_dot_1'}
                            if (item[6] == 'ky_tt_coc') {return 'ky_tt_coc'}
                            if (item[6] == 'du_dk') {return 'du_dk'}
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
                self.interval = setInterval(self.updateUnit.bind(self),2000);
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
         _format_number: function(x){
            var parts = x.toString().split(",");
            parts[0] = parts[0].replace(/\B(?=(\d{3})+(?!\d))/g, ".");
            return parts.join(",");
         },
        /**
         * @private giá từ thay đổi
         */
         _onChangeTuGia: function(event){
            event.stopPropagation();
            var temp = $(event.currentTarget).val()
            if (temp){
                temp = temp.replaceAll(".","")
                var temp_so = temp.replaceAll(",",".")
                this.filter.bsd_tu_gia =  Number(temp_so.replace(/[^0-9.-]+/g,""));
                $(event.currentTarget).val(this._format_number(temp.replace(/[^0-9.,-]+/g,"")))
            }
            else {
                this.filter.bsd_tu_gia =  null
            }
            console.log(this.filter.bsd_tu_gia)
         },
        /**
         * @private giá đến thay đổi
         */
         _onChangeDenGia: function(event){
            event.stopPropagation();
            var temp = $(event.currentTarget).val()
            if (temp){
                temp = temp.replaceAll(".","")
                var temp_so = temp.replaceAll(",",".")
                this.filter.bsd_den_gia =  Number(temp_so.replace(/[^0-9.-]+/g,""));
                $(event.currentTarget).val(this._format_number(temp.replace(/[^0-9.,-]+/g,"")))
            }
            else {
                this.filter.bsd_den_gia =  null
            }
            console.log(this.filter.bsd_den_gia)
         },
        /**
         * @private diện tích từ thay đổi
         */
         _onChangeTuDt: function(event){
            event.stopPropagation();
            var temp = $(event.currentTarget).val()
            if (temp){
                temp = temp.replaceAll(".","")
                var temp_so = temp.replaceAll(",",".")
                this.filter.bsd_tu_dt =  Number(temp_so.replace(/[^0-9.-]+/g,""))
                $(event.currentTarget).val(this._format_number(temp.replace(/[^0-9.,-]+/g,"")))
            }
            else {
                this.filter.bsd_tu_dt =  null
            }
            console.log(this.filter.bsd_tu_dt)
         },
        /**
         * @private Diện tích đến thay đổi
         */
         _onChangeDenDt: function(event){
            event.stopPropagation();
            var temp = $(event.currentTarget).val()
            if (temp){
                temp = temp.replaceAll(".","")
                var temp_so = temp.replaceAll(",",".")
                this.filter.bsd_den_dt =  Number(temp_so.replace(/[^0-9.-]+/g,""))
                $(event.currentTarget).val(this._format_number(temp.replace(/[^0-9.,-]+/g,"")))
            }
            else {
                this.filter.bsd_den_dt =  null
            }
            console.log(this.filter.bsd_den_dt)
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
            $(event.currentTarget).tooltip("dispose")
            var unit_id = parseInt($(event.currentTarget).attr('id'))
            var data_unit = _.find(this.data, function(item){return item[4] === unit_id})
            if (data_unit == undefined){
                return null
            }
            var data = {}
            data.dien_tich = data_unit[9]
            data.loai_ch = data_unit[10]
            this._rpc({
                model: 'bsd.giu_cho',
                method: 'search_read',
                fields: ['bsd_ma_gc', 'bsd_khach_hang_id', 'bsd_stt_bg',
                         'bsd_ngay_hh_gc', 'state', 'bsd_nvbh_id',
                         'bsd_san_gd_id','bsd_ctv_id','bsd_gioi_thieu_id'],
                domain: [['state', 'in', ['dat_cho','dang_cho','giu_cho']], ['bsd_unit_id', '=', data_unit[11]]]
            }).then(function(giu_cho){
                if (_.isEmpty(giu_cho)){
                    data.giu_cho = null
                }
                else {
                    _.each(giu_cho, function(item,index,giu_cho){
                        if (item.bsd_stt_bg === 0){
                            item.bsd_stt_bg = ''
                        }
                        if (item.bsd_ngay_hh_gc === false){
                            item.bsd_ngay_hh_gc = ''
                        }
                        else {
                            let time = new moment.utc(item.bsd_ngay_hh_gc)
                            item.bsd_ngay_hh_gc = time.local().format('DD/MM/YYYY HH:mm')
                        }
                        // Cập nhật môi giới
                        if (item.bsd_san_gd_id !== false){
                            console.log(item.bsd_san_gd_id)
                            item.moi_gioi = item.bsd_san_gd_id[1]
                        }
                        else if (item.bsd_ctv_id !== false){
                            console.log(item.bsd_ctv_id)
                            item.moi_gioi = item.bsd_ctv_id[1]
                        }
                        else if (item.bsd_gioi_thieu_id !== false){
                            console.log(item.bsd_gioi_thieu_id)
                            let moi_gioi = item.bsd_gioi_thieu_id[1]
                            if (moi_gioi.length > 1) {
                                item.moi_gioi = moi_gioi[1]
                            }
                            else {
                                item.moi_gioi = moi_gioi[0]
                            }
                        }
                        else {
                            item.moi_gioi = ''
                        }
                        console.log(item.moi_gioi)
                    })
                    data.giu_cho = giu_cho
                }
                var title = qweb.render('bsd_sale_chart.tooltip', {'data':data})
                var template = qweb.render('bsd_sale_chart.template_tooltip', {'data': data_unit})
                $(event.currentTarget).tooltip({
                    template: template,
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
         * @private Click mở giữ chỗ
         */
         _clickMoGiuCho: function(event){
            event.stopPropagation()
            var self = this
            var giu_cho_id = parseInt($(event.currentTarget).attr('id'))
            this._loadAction('bsd_sale_chart.bsd_giu_cho_action_2').then(function(action){
                action.res_id = giu_cho_id
                action.flags={'mode': 'readonly'}
                self.do_action(action)
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
         _clickQuanTam: function(event){
            event.stopPropagation()
            var self = this
            var unit_id = parseInt($(event.currentTarget).parent().attr('id'))
            this._loadAction('bsd_sale_chart.bsd_quan_tam_action').then(function(action){
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
            let unit_id = parseInt($(event.currentTarget).parent().attr('id'))
            this._loadAction('bsd_sale_chart.bsd_bao_gia_action_popup_2').then(function(action){
                action.context={default_bsd_unit_id:unit_id}
                console.log(action)
                self.do_action(action)
            })
//            this.do_action({
//                name: "Tạo bảng tính giá",
//                res_model: 'bsd.bao_gia',
//                views: [[false, 'form']],
//                type: 'ir.actions.act_window',
//                view_mode: "form",
//                target: "new"
//            })
         },
        /**
         * @private Thay đổi dự án đợt mở bán
         */
        _onFieldChange: function(event){
            event.stopPropagation();
            var fieldName = event.target.name;
            console.log("field name")
            console.log(fieldName)
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
            else if (fieldName === 'bsd_view_ids'){
                if (event.data.changes.bsd_view_ids !== false){
                    var bsd_view_ids = event.data.changes.bsd_view_ids;
                    this.trigger_up('change_view', {'data':bsd_view_ids})
                }
                else {
                    var bsd_view_ids = event.data.changes.bsd_view_ids;
                    this.trigger_up('change_view', {'data':bsd_view_ids})
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
            if (dataChange.field === 'bsd_view_ids'){
                var list_id = []
                if (_.isArray(dataChange.data.ids)){
                    _.each(dataChange.data.ids, function(item,index,data){
                    list_id.push(item.id)
                    })
                }
                else if (_.isObject(dataChange.data.ids)) {
                    list_id.push(dataChange.data.ids.id)
                }
                else {
                    list_id.push(dataChange.data.ids)
                }
                dataChange.data.ids = []
                self._rpc({
                    model: 'bsd.view',
                    method: 'search_read',
                    fields: ['bsd_ten'],
                    domain: [['id', 'in', list_id]],
                    context: self.context
                }).then(function (data){
                    _.each(data, function(item, index,data){
                        let temp = {id:item.id, display_name:item.bsd_ten}
                        dataChange.data.ids.push(temp)
                    })
                }).then(function(){
                    console.log("dataChange")
                    console.log(dataChange.data.ids)
                    self._makeRecord(dataChange).then(function (recordID) {
                        console.log("có chạy code ở đây ko")
                        self.fields.bsd_view_ids.reset(self.model.get(recordID));
                    });
                })
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
                    domain: [['state', '=', 'phat_hanh']]
                },
                {
                    relation: 'bsd.dot_mb',
                    type: 'many2one',
                    name: 'bsd_dot_mb_id',
                    domain: [['bsd_du_an_id', '=', self.filter.bsd_du_an_id]]
                },
                {
                    relation: 'bsd.view',
                    type: 'many2many',
                    name: 'bsd_view_ids',
                    value: []
                },
                {
                    type: 'char',
                    name: 'bsd_unit',
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
                    type: 'char',
                    name: 'bsd_tu_gia',
                },
                {
                    type: 'char',
                    name: 'bsd_den_gia',
                },
                {
                    type: 'char',
                    name: 'bsd_tu_dt',
                },
                {
                    type: 'char',
                    name: 'bsd_den_dt',
                },
            ];
            if (data != null && data.data != null){
                if (data.field === 'bsd_dot_mb_id'){
                    field[1].value = [data.data.id, data.data.display_name];
                }
                if (data.field === 'bsd_du_an_id'){
                    field[0].value = [data.data.id, data.data.display_name];
                    field[1].domain = [['bsd_du_an_id', '=', data.data.id]]
                }
                if (data.field === 'bsd_view_ids'){
                    if (data.data.operation === 'ADD_M2M'){

//                        if (_.isArray(data.data.ids)){
                        _.each(data.data.ids, function(item,index,data){
                            self.filter.bsd_view_ids.push(item)
                        })
                        field[2].value = self.filter.bsd_view_ids
                    }
                    if (data.data.operation === 'FORGET'){
                        self.filter.bsd_view_ids = self.filter.bsd_view_ids.filter(el => el.id != data.data.ids[0].id )
                        field[2].value = self.filter.bsd_view_ids
                    }

                }
            }
            return this.model.makeRecord('bsd.sale_chart.widget', field, {});
        },
    });
    return {
        SaleChartRenderer: SaleChartRenderer,
    };
})