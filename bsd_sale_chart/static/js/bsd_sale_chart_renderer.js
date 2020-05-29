odoo.define('bsd_sale_chart.SaleChartRenderer', function(require){
'use strict';
    var Widget = require('web.Widget');
    var FieldManagerMixin = require('web.FieldManagerMixin');
    var relational_fields = require('web.relational_fields');
    var basis_fields = require('web.basic_fields');
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
            this.filter = {
                bsd_du_an_id: null,
                bsd_dot_mb_id: null
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
                    )
                };
                self.fields.bsd_du_an_id.appendTo(self.$('.create_du_an_id .o_td_field'))
                self.fields.bsd_dot_mb_id.appendTo(self.$('.create_dot_mb_id .o_td_field'))
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
//            console.log("on search in action")
//            console.log(event)
//            console.log(self.filter)
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
                var data_filter = _.each(data, function(item,index,data){
                    if (item[7] === null){
                        item[7] = 0
                    }
                    if (item[8] !== null){
                        item[8] = format_curency(item[8])
                    }
                })
                var group_toa = _.groupBy(data, function(data_filter) { return data_filter[0]});
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
                $(event.currentTarget).find("i").removeClass("fa-search-plus").addClass("fa-search-minus")
            }
            else{
                $(event.currentTarget).find("i").removeClass("fa-search-minus").addClass("fa-search-plus")
            }
         },
        /**
         * @private
         */
        _onCollapseTang: function(event){
            console.log("click on collapse")
            var t =$(event.target).parent().find(".collapse")
            if (!t.hasClass("show")){
                console.log("show")
                $(event.target).find("i").removeClass("fa-plus").addClass("fa-minus")
            }
            else{
                console.log("hide")
                $(event.target).find("i").removeClass("fa-minus").addClass("fa-plus")
            }
         },
        _onFieldChange: function(event){
            event.stopPropagation();
            var fieldName = event.target.name;
            if (fieldName === 'bsd_du_an_id'){
                var bsd_du_an_id = event.data.changes.bsd_du_an_id;
                this.trigger_up('change_du_an', {'data':bsd_du_an_id})
            }
            if (fieldName === 'bsd_dot_mb_id'){
                var bsd_dot_mb_id = event.data.changes.bsd_dot_mb_id;
                this.trigger_up('change_dot_mb', {'data':bsd_dot_mb_id})
            }
        },

        update: function(dataChange){
            console.log("update in rendder");
            console.log(dataChange);
            var t = null;
            var self = this;
            if (dataChange.field === 'bsd_dot_mb_id'){
                this._makeRecord(dataChange).then(function (recordID) {
                    self.filter.bsd_dot_mb_id = dataChange.data.id
                    self.fields.bsd_dot_mb_id.reset(self.model.get(recordID));
                });
            };
            if (dataChange.field === 'bsd_du_an_id'){
                this._makeRecord(dataChange).then(function (recordID) {
                    self.filter.bsd_du_an_id = dataChange.data.id
                    self.fields.bsd_du_an_id.reset(self.model.get(recordID));
                });
            };
        },
    /**
     * @private
     * @returns {string} local id of the dataPoint
     */
        _makeRecord: function (data = null) {
            var field = [{
                    relation: 'bsd.du_an',
                    type: 'many2one',
                    name: 'bsd_du_an_id',
                },
                {
                    relation: 'bsd.dot_mb',
                    type: 'many2one',
                    name: 'bsd_dot_mb_id',
                },
            ];
            if (data != null){
                if (data.field === 'bsd_dot_mb_id'){
                    field[1].value = [data.data.id, data.data.display_name];
                }
                if (data.field === 'bsd_du_an_id'){
                    field[0].value = [data.data.id, data.data.display_name];
                }
            }
            return this.model.makeRecord('bsd.sale_chart.widget', field, {});

        },
    });
    return {
        SaleChartRenderer: SaleChartRenderer,
    };
})