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
                this.$buttons.find('.oe_tt_button').click(this.proxy('action_tao_tt'));
            }
        },
        action_tao_tt: function(){
            var self = this
            var user = session.uid
            console.log("Bấm ăn rui nè")
            console.log(session)
        }
    })
})