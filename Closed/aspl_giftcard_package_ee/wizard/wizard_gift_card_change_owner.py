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
from odoo.exceptions import UserError, ValidationError
from datetime import datetime


class UseGiftCard(models.TransientModel):
    _name = 'gift.card.change.owner.wizard'
    _description = 'Gift Card Change Owner Wizard'

    gift_card_id = fields.Char(string="Card Number", default=lambda self: self.env['gift.card'].browse(self.env.context.get('active_id')).card_no)
    partner_id = fields.Char(string="Card Owner", default=lambda self: self.env['gift.card'].browse(self.env.context.get('active_id')).customer_id.name)
    new_partner_id = fields.Many2one("res.partner", string="New Owner")

    def change_gift_card_owner(self):
        ctx = self._context.copy()
        gift_card_id = self.env['gift.card'].browse(ctx.get('active_id'))
        if self.new_partner_id and gift_card_id:
            history_vals = {
                'customer_id': gift_card_id.customer_id.id,
                'card_id': gift_card_id.id,
                'new_customer_id': self.new_partner_id.id,
                'user_id': self.env.user.id,
                'card_amount': gift_card_id.balance,
            }
            self.env['gift.owner.history'].create(history_vals)
            gift_card_id.write({
                'customer_id': self.new_partner_id.id
            })
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: