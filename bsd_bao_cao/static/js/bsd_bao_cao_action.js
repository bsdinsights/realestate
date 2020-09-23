odoo.define('bsd_bao_cao.BaoCaoAction', function(require){
    "use strict";
    var AbstractAction = require('web.AbstractAction');
    var SaleChartRenderer = require('bsd_bao_cao.SaleChartRenderer')
    var SaleChartModel = require('bsd_bao_cao.SaleChartModel')
    var core = require('web.core');
    var Qweb = core.qweb;

    var BaoCaoAction = AbstractAction.extend({
        hasControlPanel: false,
        custom_events:{
            change_du_an: '_onAction',
        },
        contentTemplate: 'bsd_bao_cao.bao_cao',
        config: _.extend({}, AbstractAction.prototype.config,{
            SaleChartRenderer: SaleChartRenderer.SaleChartRenderer,
            Model: SaleChartModel.SaleChartModel,
        }),
        init: function(parent,params){
            this._super.apply(this, arguments);
            this.model = new this.config.Model(this, {
                modelName: "bsd.bao_cao.widget"
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
            if (event.name === 'change_du_an'){
                event.data.field = 'bsd_du_an_id',
                self.renderer.update(event.data)
            }
        },
        reload: function () {
            window.location.href = this.href;
        },
    });
    core.action_registry.add('bao_cao_view', BaoCaoAction);

    return {
        BaoCaoAction: BaoCaoAction,
    }
});

