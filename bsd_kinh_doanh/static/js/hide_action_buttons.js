//odoo.define('hide_action_buttons.hide_action_buttons', function (require) {
//    "use strict";
//    var FormController = require('web.FormController');
//    FormController.include({
//        renderButtons: function($node){
//            this._super.apply(this, arguments)
//            var data = this.model.get(this.handle).data
//            console.log(data)
//            console.log(data.hide_action_buttons)
//            if (data.hide_action_buttons) {
//                this.$buttons.find('.o_form_buttons_view').hide();
//            }
//            else {
//                this.$buttons.find('.o_form_buttons_view').show();
//            }
//        }
//    });
//});