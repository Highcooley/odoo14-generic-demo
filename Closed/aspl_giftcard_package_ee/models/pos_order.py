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
import logging
from odoo import models, fields, api, tools, _

_logger = logging.getLogger(__name__)


class PosOrder(models.Model):
    _inherit = 'pos.order'

    @api.model
    def _process_order(self, order, draft, existing_order):
        order_id = super(PosOrder, self)._process_order(order, draft, existing_order)
        if order_id:
            if order.get('data').get('giftcard'):
                for create_details in order.get('data').get('giftcard'):
                    gift_card_id = self.env['gift.card'].create(create_details)
                    gift_card_id.write({'state': 'confirm'})
            #  create redeem giftcard for use
            pos_order = False
            if order_id:
                pos_order = self.browse(order_id)
            if order.get('data').get('redeem') and pos_order:
                redeem_details = order.get('data').get('redeem')
                redeem_vals = {
                    'pos_order_id': pos_order.id,
                    'order_date': pos_order.date_order,
                    'partner_id': int(redeem_details.get('card_customer_id')) or False,
                    'card_id': redeem_details.get('redeem_card_no'),
                    'amount': redeem_details.get('redeem_card_amount'),
                }
                use_giftcard = self.env['gift.card.use'].create(redeem_vals)
            # recharge giftcard
            if order.get('data').get('recharge') and pos_order:
                recharge_details = order.get('data').get('recharge')
                # for recharge_details in order.get('recharge'):
                recharge_vals = {
                    'user_id': pos_order.user_id.id,
                    'recharge_date': pos_order.date_order,
                    'customer_id': int(recharge_details.get('card_customer_id')) or False,
                    'card_id': recharge_details.get('recharge_card_id'),
                    'amount': recharge_details.get('recharge_card_amount'),
                }
                recharge_giftcard = self.env['gift.card.recharge'].create(recharge_vals)
                if recharge_giftcard:
                    recharge_giftcard.card_id.write(
                        {'card_value': recharge_giftcard.card_id.card_value + recharge_giftcard.amount})
        return order_id

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: