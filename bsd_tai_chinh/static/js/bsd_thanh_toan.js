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
                this.$buttons.find('.oe_tt_tt_button').click(this.proxy('action_tt_tt'));
                this.$buttons.find('.oe_tt_gctc_button').click(this.proxy('action_tt_gctc'));
                this.$buttons.find('.oe_tt_gc_button').click(this.proxy('action_tt_gc'));
                this.$buttons.find('.oe_tt_dc_button').click(this.proxy('action_tt_dc'));
            }
        },
        action_tt_hd: function(){
            var self = this
            var user = session.uid
            this._loadAction('bsd_tai_chinh.bsd_wizard_tt_dot_action_2').then(function(action){
                action.flags = {new_window: false}
                self.do_action(action)
            })
        },
        action_tt_tt: function(){
            var self = this
            var user = session.uid
            this._loadAction('bsd_tai_chinh.bsd_phieu_thu_action_popup_tra_truoc').then(function(action){
                action.context={'default_bsd_loai_pt': 'tra_truoc'}
                self.do_action(action)
            })
        },
        action_tt_gctc: function(){
            var self = this
            var user = session.uid
            this._loadAction('bsd_tai_chinh.bsd_wizard_tt_gc_tc_action').then(function(action){
                self.do_action(action)
            })
        },
        action_tt_gc: function(){
            var self = this
            var user = session.uid
            this._loadAction('bsd_tai_chinh.bsd_wizard_tt_giu_cho_action').then(function(action){
                self.do_action(action)
            })
        },
        action_tt_dc: function(){
            var self = this
            var user = session.uid
            this._loadAction('bsd_tai_chinh.bsd_wizard_tt_dat_coc_action').then(function(action){
                self.do_action(action)
            })
        },
    })
})