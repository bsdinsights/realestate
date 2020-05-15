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
        template: 'bsd_sale_chart.sale_chart',
        events: {
            'click #search' : '_onSearch',
        },
        /**
         * @override
         */
         init: function(parent, model, state){
            console.log("init trong renderer")
            console.log(state)
            this._super(parent);
            this.model = model;
            this._initialState = state
         },
        /**
         * @override
         */
        start: function () {
            var self = this;
            var def1 = this._makePartnerRecord(16, 'Sundihome 6').then(function (recordID) {
                self.fields = {
                    bsd_du_an_id : new relational_fields.FieldMany2One(self,
                        'bsd_du_an_id',
                        self.model.get(recordID), {
                            mode: 'edit',
                            attrs: {
                                placeholder: _t('Chọn dự án'),
                            }
                        }
                    ),
                    bsd_dot_mb_id : new relational_fields.FieldMany2One(self,
                        'bsd_dot_mb_id',
                        self.model.get(recordID), {
                            mode: 'edit',
                            attrs: {
                                placeholder: _t('Chọn đợt mở bán'),
                            }
                        }
                    )
                };
                self.fields.bsd_du_an_id.appendTo(self.$('.create_du_an_id .o_td_field'))
                self.fields.bsd_dot_mb_id.appendTo(self.$('.create_dot_mb_id .o_td_field'))
            });
            console.log("start in renderer")
            console.log(def1)
            var def2 = this._super.apply(this, arguments);
            return Promise.all([def1, def2]);
        },

        /**
         * @private
         */
        _onSearch: function(){
            console.log("on search in ")
            this.trigger_up('search')
         },
    /**
     * @private
     * @param {integer} partnerID
     * @param {string} partnerName
     * @returns {string} local id of the dataPoint
     */
        _makePartnerRecord: function (partnerID, partnerName) {
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
            if (partnerID) {
                field.value = [partnerID, partnerName];
            }
            return this.model.makeRecord('bsd.sale_chart.widget', field, {
                partner_id: {
                    domain: [],
                    options: {
                        no_open: true
                    }
                }
            });
        },
    });
    return {
        SaleChartRenderer: SaleChartRenderer,
    };
})