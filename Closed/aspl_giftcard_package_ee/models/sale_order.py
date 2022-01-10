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
import time
import datetime
import logging
from odoo import models, fields, api, _
from odoo.exceptions import AccessError, UserError, ValidationError
_logger = logging.getLogger(__name__)


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    gift_card_value = fields.Float(string="Gift Card Amount")
    gift_card_id = fields.Many2one('gift.card', string="Gift Card")
    gift_card_use_ids = fields.One2many('gift.card.use', 'order_id', string="Gift Card Use")
    receiver_email = fields.Char(string="Receiver Email")
    receiver_name = fields.Char(string="Receiver Name")
    gift_card_ids = fields.One2many('gift.card', 'order_id', string="Use Gift Card")
    is_gift_card_add = fields.Boolean("Gift Card Add")
    new_gift_card_id = fields.Many2one('gift.card', string="New Gift Card", copy=False)

    @api.onchange('order_line')
    def _onchnage_order_line(self):
        order_line = self.order_line.filtered(lambda line: line.product_id.id == self.env.company.gift_card_product_id.id)
        if order_line and len(order_line) > 1:
            raise ValidationError(_('You are allow to sale only 1 gift card for particular order.'))
        if order_line and order_line.product_uom_qty > 1 or order_line and order_line.product_uom_qty < 1 :
            raise ValidationError(_('You are allow to sale only 1 gift card for particular order.'))

    def action_confirm(self):
        order_line = self.order_line.filtered(lambda line: line.product_id.id == self.env.company.gift_card_product_id.id)
        if self.order_line and self.website_id:
            for line in order_line:
                if line.price_unit > 0:
                    gift_card_value = line.price_unit
                    gift_card_vals = {
                        'card_value': gift_card_value,
                        'customer_id': self.partner_id.id,
                    }
                    card_id = self.env['gift.card'].create(gift_card_vals)
                    card_id.state = 'confirm'
        if not self.new_gift_card_id and not self.website_id:
            if order_line:
                gift_card_value = order_line.price_unit
                if self.env.company.menual_card_number:
                    return {
                        'name': _('Gift Card Number'),
                        'type': 'ir.actions.act_window',
                        'res_model': 'wizard.create.gift.card',
                        'view_mode': 'form',
                        'target': 'new',
                        'context': {'default_order_line': order_line.id,}
                    }
                else:
                    gift_card_vals = {
                        'card_value': gift_card_value,
                        'customer_id': self.partner_id.id,
                    }
                    card_id = self.env['gift.card'].create(gift_card_vals)
                    self.new_gift_card_id = card_id.id
                    order_line.qty_delivered = 1
                    return super(SaleOrder, self).action_confirm()
            else:
                return super(SaleOrder, self).action_confirm() 
        else:
            return super(SaleOrder, self).action_confirm() 

    def _prepare_invoice(self):
        result = super(SaleOrder, self)._prepare_invoice()
        order_line = self.order_line.filtered(lambda line: line.product_id.id == self.env.company.gift_card_product_id.id)
        if order_line:
            result.update({
                'new_gift_card_id': self.new_gift_card_id.id
            })
        return result

    # def write(self, vals):
    #     for so in self:
    #         if vals.get('state') == 'sale' or vals.get('state') == 'done':
    #             sale_order_line_id = self.env['sale.order.line'].search([('order_id', '=', so.id),
    #                                                                      ('product_id.is_gift_card', '=', True)])
    #             if sale_order_line_id:
    #                 if not so.gift_card_id:
    #                     qty = sale_order_line_id.product_uom_qty
    #                     gift_card_value = sale_order_line_id.price_subtotal / qty
    #                     while qty > 0:
    #                         gift_card_obj = self.env['gift.card']
    #                         gift_card_obj.create({
    #                             'card_value': gift_card_value,
    #                             'customer_id': self.env.user.partner_id.id,
    #                             'email': so.receiver_email,
    #                             'user_name': so.receiver_name
    #                         })
    #                         qty -= 1
    #                         time.sleep(2)
    #                 if so.gift_card_id:
    #                     gift_card_obj = self.env['gift.card'].search([('id', '=', so.gift_card_id.id)])
    #                     if gift_card_obj:
    #                         gift_card_obj.write({
    #                             'card_value': gift_card_obj.card_value + sale_order_line_id.price_subtotal,
    #                             'recharge_line': [(0, 0, {'card_id': so.gift_card_id.id,
    #                                                       'amount': sale_order_line_id.price_subtotal})]
    #                         })
    #         res = super(SaleOrder, self).write(vals)
    #         return res
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
