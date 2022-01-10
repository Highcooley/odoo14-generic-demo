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
from odoo import models, fields, api, _


class ResCompany(models.Model):
    _inherit = 'res.company'

    is_gift_card = fields.Boolean('Enable Website Gift Card')
    gift_card_product_id = fields.Many2one('product.product', string="Gift Card Product")
    gift_card_account_id = fields.Many2one('account.account', string="Gift Card Account")
    gc_journal_id = fields.Many2one('account.journal', string="Gift Card Journal")
    default_exp_month = fields.Integer('Default Card Expire Months')
    menual_card_number = fields.Boolean('Enable Menual Card Number')
    
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
