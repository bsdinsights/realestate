odoo.define('bsd_sale_chart.SaleChartAction', function(require){
    "use strict";
    var AbstractAction = require('web.AbstractAction');
    var SaleChartRenderer = require('bsd_sale_chart.SaleChartRenderer')
    var SaleChartModel = require('bsd_sale_chart.SaleChartModel')
    var core = require('web.core');
    var Qweb = core.qweb;

    var SaleChartAction = AbstractAction.extend({
        hasControlPanel: true,
        custom_events:{
            search : '_onAction',
        },
        contentTemplate: 'bsd_sale_chart.reconciliation',
        config: _.extend({}, AbstractAction.prototype.config,{
            SaleChartRenderer: SaleChartRenderer.SaleChartRenderer,
            Model: SaleChartModel.SaleChartModel,
        }),
        init: function(parent,params){
            console.log("Init trong action")
            this._super.apply(this, arguments);
            this.model = new this.config.Model(this, {
                modelName: "bsd.sale_chart.widget"
            });
            this.renderer = new this.config.SaleChartRenderer(this, this.model);
            this.widgets = [];
        },

        _renderLines: function () {
            console.log("render line in action")
            var self = this;
            var linePromises = [];
            var widget = new self.config.SaleChartRenderer(self, self.model);
            self.widgets.push(widget);
            var t = Promise.all(linePromises);
            console.log("render line in action")
            return t
        },

        start: function() {
            var self = this;
            var args = arguments;
            var sup = this._super;

            return this.renderer.prependTo(self.$('.o_form_sheet_bg')).then(function(){
                return self._renderLines().then(function(){
                    return sup.apply(self,args);
                })
            });
        },

        _onAction: function(event){
            console.log("on action")
            this.model[_.str.camelize(event.name)]()
        },

        render: function(){
            var self = this;
            self.select_project()
        },
        select_project: function(){
            var self = this
            var s = $('#chon_du_an')
            _.each(self.data, function (item,index,data){
                console.log(item.bsd_ten_da)
                var optionValue = item.id;
                var optionText = item.bsd_ten_da;
                s.append(`<option value="${optionValue}">${optionText}</option>`)
            })
            self.drawChart(parseInt(s.val()),$("#select option:selected").text())
            s.change(function(){
                self.drawChart(parseInt(s.val()),$("#select option:selected").text())
            })
        },
        drawChart: function (id_project,name_project) {
            var self = this
            self._rpc({
                model: 'bsd.toa_nha',
                method: 'search_read',
                fields: ['id','bsd_ma_ht'],
                domain: [['bsd_du_an_id', '=',id_project]]
            }).then(function (data_block){
                var ids_block = []
                _.each(data_block, function(item,index,data_block){
                    ids_block.push(item.id)
                })
                self._rpc({
                    model: 'bsd.tang',
                    method: 'search_read',
                    fields: ['id','bsd_ma_tang','bsd_toa_nha_id'],
                    domain: [['bsd_toa_nha_id', 'in', ids_block]]
                }).then(function(data_floor){
                    _.each(data_floor, function(item,index,data_floor){
                    })
                    self._rpc({
                        model: 'product.product',
                        method: 'search_read',
                        fields: ['id','name'],
                        domain: [['bsd_du_an_id', '=', id_project]]
                    }).then(function(data_unit){
                        _.each(data_unit, function(item,index,data_unit){
                        })
                    })
                })

            })
        },
        reload: function () {
            window.location.href = this.href;
    },
    });
    core.action_registry.add('sale_chart_view', SaleChartAction);

    return {
        SaleChartAction: SaleChartAction,
    }
});

