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

from odoo import models,fields,api,_


class WizardCreateGiftCard(models.TransientModel):
    _name = 'wizard.create.gift.card'
    _description = 'Wizard Create Gift Card'

    card_number = fields.Char(string="Card Number", required=True)
    card_type = fields.Many2one('gift.card.type', string="Card Type")
    order_line = fields.Many2one('sale.order.line', string="Order line")

    def create_new_gift_card(self):
        ctx = self._context.copy()
        gift_card_vals = {
            'card_no': self.card_number,
            'card_value': self.order_line.price_unit,
            'card_type': self.card_type.id,
            'customer_id': self.order_line.order_id.partner_id.id,
        }
        card_id = self.env['gift.card'].create(gift_card_vals)
        self.order_line.order_id.new_gift_card_id = card_id.id
        self.order_line.qty_delivered = 1
        self.order_line.order_id.action_confirm()
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: