odoo.define('bsd_sale_chart.SaleChartModel', function (require) {
"use strict";

    var BasicModel = require('web.BasicModel');
    var field_utils = require('web.field_utils');
    var utils = require('web.utils');
    var session = require('web.session');
    var WarningDialog = require('web.CrashManager').WarningDialog;
    var core = require('web.core');
    var _t = core._t;

    var SaleChartModel = BasicModel.extend({
        init: function (parent, options) {
            this._super.apply(this, arguments);
        },
        search: function(){
        }

    });

    return {
        SaleChartModel: SaleChartModel,
    };

})
