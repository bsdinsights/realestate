odoo.define('phieu_thu.tao_thanh_toan', function(require){
"use strict";
var core = require('web.core');
var ListController = require('web.ListController');
var session = require('web.session');
var _t = core._t;
    ListController.include({
        renderButtons: function($node){
            this._super.apply(this, arguments)
            if (this.$buttons){
                this.$buttons.find('.oe_tt_hd_button').click(this.proxy('action_tt_hd'));
            }
        },
        action_tt_hd: function(){
            var self = this
            var user = session.uid
            this._loadAction('bsd_tai_chinh.bsd_wizard_tt_dot_action_2').then(function(action){
                action.flags = {new_window: false}
                self.do_action(action)
            })
        }
    })
})