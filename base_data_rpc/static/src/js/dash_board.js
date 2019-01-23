// rpc仪表盘
odoo.define('base_data_rpc.rpc.dash.board', function (require) {
    "use strict";

    let core = require('web.core');
    let _t = core._t;
    let QWeb = core.qweb;
    let Widget = require('web.Widget');
    let Model = require('web.Model');
    let RpcDashBoard = Widget.extend({

        start: function () {
            let self = this;
            self.$el.html(QWeb.render("BaseRPCDashBoard", {widget: self}));
        }
    });
    core.action_registry.add('rpc_dash_board', RpcDashBoard);
    return RpcDashBoard;
});
