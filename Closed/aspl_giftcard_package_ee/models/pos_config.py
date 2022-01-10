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
from odoo import models, fields, api


class POSConfig(models.Model):
    _inherit = 'pos.config'

    def _get_group_erp_manager(self):
        return self.env.ref('base.group_erp_manager')

    enable_gift_card = fields.Boolean('Gift Card')
    gift_card_product_id = fields.Many2one('product.product', string="Gift Card Product")
    enable_journal_id = fields.Many2one('pos.payment.method', string="Enable Journal")
    msg_before_card_pay = fields.Boolean('Confirm Message Before Card Payment')
    group_admin_user_id = fields.Many2one('res.groups', string='Administrator User Group', default=_get_group_erp_manager,
        help='This field is there to pass the id of the admin user group to the point of sale client.')

    
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
