odoo.define('aspl_giftcard_package_ee.giftCardChangeOwnerPopup', function(require) {
    'use strict';

    const { useState, useRef } = owl.hooks;
    const AbstractAwaitablePopup = require('point_of_sale.AbstractAwaitablePopup');
    const Registries = require('point_of_sale.Registries');
    var core = require('web.core');
    var _t = core._t;
    
    class giftCardChangeOwnerPopup extends AbstractAwaitablePopup {
        constructor() {
            super(...arguments);
            this.state = useState({ SelectCustomer: ''});
        }
        getPayload() {
            this.state.SelectCustomer = $('option[value="'+$('#select_customer').val()+'"]').attr('id')
            return {new_owner:this.state.SelectCustomer};
        }
        async confirm() {
            var SelectCustomer = $('option[value="'+$('#select_customer').val()+'"]').attr('id')
            if (SelectCustomer && this.state.SelectCustomer) {
                this.props.resolve({ confirmed: true, payload: await this.getPayload()});
                this.trigger('close-popup');
            }else{
                this.env.pos.db.notification('danger', _t('Please Select Customer!'));
                return false;
            }
        }
    }
    giftCardChangeOwnerPopup.template = 'giftCardChangeOwnerPopup';
    giftCardChangeOwnerPopup.defaultProps = {
        confirmText: 'Extend',
        cancelText: 'Cancel',
        title: '',
        body: '',
    };

    Registries.Component.add(giftCardChangeOwnerPopup);

    return giftCardChangeOwnerPopup;
});
