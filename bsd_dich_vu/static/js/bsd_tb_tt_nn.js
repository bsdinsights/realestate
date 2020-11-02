odoo.define('tb_tt.tao_thong_bao', function(require){
"use strict";
var core = require('web.core');
var ListController = require('web.ListController');
var session = require('web.session');
var _t = core._t;
    ListController.include({
        renderButtons: function($node){
            this._super.apply(this, arguments)
            if (this.$buttons){
                this.$buttons.find('.oe_tao_td_button').click(this.proxy('action_tao_tb'));
                this.$buttons.find('.oe_tao_td_nn_button').click(this.proxy('action_tao_tb_nn'));
            }
        },
        action_tao_tb: function(){
            var self = this
            var user = session.uid
            this._loadAction('bsd_dich_vu.bsd_wizard_tao_tb_tt_action_2').then(function(action){
                action.context={default_bsd_loai:'tb_tt'}
                self.do_action(action)
            })
        },
        action_tao_tb_nn: function(){
            var self = this
            var user = session.uid
            this._loadAction('bsd_dich_vu.bsd_wizard_tao_tb_tt_action_2').then(function(action){
                action.context={default_bsd_loai:'tb_nn'}
                self.do_action(action)
            })
        },
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
    })
})