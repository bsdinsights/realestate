odoo.define('bsd_sale_chart.SaleChartAction', function(require){
    "use strict";
    var AbstractAction = require('web.AbstractAction');
    var SaleChartRenderer = require('bsd_sale_chart.SaleChartRenderer')
    var SaleChartModel = require('bsd_sale_chart.SaleChartModel')
    var core = require('web.core');
    var Qweb = core.qweb;

    var SaleChartAction = AbstractAction.extend({
        hasControlPanel: false,
        custom_events:{
            change_du_an: '_onAction',
            change_dot_mb: '_onAction',
        },
        contentTemplate: 'bsd_sale_chart.gio_hang',
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

        start: function() {
            var self = this;
            var args = arguments;
            var sup = this._super;

            return this.renderer.prependTo(self.$('.o_form_sheet_bg')).then(function(){
                    return sup.apply(self,args);
            });
        },

        _onAction: function(event){
            var self = this;
            console.log("on action")
            console.log(event)
            if (event.name === 'change_du_an'){
                event.data.field = 'bsd_du_an_id',
                self.renderer.update(event.data)
            }
            else if (event.name === 'change_dot_mb'){
                event.data.field = 'bsd_dot_mb_id',
                self.renderer.update(event.data)
            }
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

