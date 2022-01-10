# -*- coding: utf-8 -*-
#################################################################################
# Author      : Acespritech Solutions Pvt. Ltd. (<www.acespritech.com>)
# Copyright(c): 2012-Present Acespritech Solutions Pvt. Ltd.
# All Rights Reserved.
#
# This program is copyright property of the author mentioned above.
# You can`t redistribute it and/or modify it.
#
#################################################################################
{
    'name': "POS Gift Card (Enterprise)",
    'summary': "This module allows user to purchase giftcard, use giftcard and also recharge giftcard.",
    'description': """
        User can purchase giftcard, use giftcard and also recharge giftcard. 
    """,
    'category': 'Point of Sale',
    'author': 'Acespritech Solutions Pvt. Ltd.',
    'website': "http://www.acespritech.com",
    'version': '1.0.2.1',
    'depends': ['base', 'point_of_sale', 'sale', 'sale_management', 'account', 'website_sale'],
    'price': 30,
    'currency': 'EUR',
    'data': [
        'security/ir.model.access.csv',
        'security/gift_card_rule.xml',
        'data/product_data.xml',
        'data/account_data.xml',
        'data/mail_template.xml',
        'data/ir_cron.xml',
        'wizard/wizard_gift_card_change_owner.xml',
        'views/gift_card_backend_view.xml',
        'wizard/wizard_gift_card_use_view.xml',
        'wizard/wizard_import_gift_card.xml',
        'wizard/wizard_create_gift_card.xml',
        'views/pos_config_view.xml',
        'views/gift_card_assets.xml',
        'views/gift_card.xml',
        'views/pos_payment_method_view.xml',
        'views/res_company_view.xml',
        'views/account_journal_view.xml',
        'views/sale_order_view.xml',
        'views/account_move_view.xml',

        
    ],
    'qweb': [
        'static/src/xml/Screens/ProductScreen/ControlButtons/giftCardControlButton.xml',
        'static/src/xml/Screens/GiftCardScreen/GiftCardScreen.xml',
        'static/src/xml/Screens/GiftCardScreen/GiftCardLine.xml',
        'static/src/xml/Screens/GiftCardScreen/giftCardCreateScreen.xml',
        'static/src/xml/Popups/giftCardCreatePopupConform.xml',
        'static/src/xml/Popups/giftCardRedeemPopup.xml',
        'static/src/xml/Popups/giftCardEditExpirePopup.xml',
        'static/src/xml/Popups/giftCardExchangePopup.xml',
        'static/src/xml/Popups/giftCardRechargePopup.xml',
        'static/src/xml/Screens/PaymentScreen/PaymentScreen.xml',
        'static/src/xml/Screens/ReceiptScreen/OrderReceipt.xml',
        'static/src/xml/Popups/giftCardChangeOwnerPopup.xml',
    ],
    'images': ['static/description/main_screenshot.png'],
    "installable": True,
    'auto_install': False,
}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
