odoo.define('aspl_giftcard_package_ee.giftCardControlButton', function(require) {
    'use strict';

    const PosComponent = require('point_of_sale.PosComponent');
    const ProductScreen = require('point_of_sale.ProductScreen');
    const { useListener } = require('web.custom_hooks');
    const Registries = require('point_of_sale.Registries');

    class giftCardControlButton extends PosComponent {
        constructor() {
            super(...arguments);
            useListener('click', this.onClick);
        }
        async onClick() {
            this.showScreen('GiftCardScreen');
        }
    }
    giftCardControlButton.template = 'giftCardControlButton';

    ProductScreen.addControlButton({
        component: giftCardControlButton,
        condition: function() {
            return this.env.pos.config.enable_gift_card && this.env.pos.user.role == 'manager' || this.env.pos.config.enable_gift_card && this.env.pos.user.admin_role == 'admin';
        },
    });

    Registries.Component.add(giftCardControlButton);

    return giftCardControlButton;
});
