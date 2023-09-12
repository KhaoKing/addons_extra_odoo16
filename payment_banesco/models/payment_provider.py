
import logging
import uuid

import requests
from werkzeug.urls import url_encode, url_join, url_parse

from odoo import _, api, fields, models
from odoo.exceptions import UserError, ValidationError

from odoo.addons.payment_banesco import utils as banesco_utils

_logger = logging.getLogger(__name__)

class PaymentProvider(models.Model):
    _inherit = 'payment.provider'

    code = fields.Selection(
        selection_add=[('banesco', "Banesco")], ondelete={'banesco': 'set default'})
    banesco_API_key = fields.Char(
        string='Banesco API Key', required_if_provider='banesco', groups='base.group_system')
    banesco_secret_key = fields.Char(
        string='Banesco Secret Key', required_if_provider='banesco', groups='base.group_system')
    
    def _compute_feature_support_fields(self):
        """ Override of `payment` to enable additional features. """
        super()._compute_feature_support_fields()
        self.filtered(lambda p: p.code == 'banesco').update({
            'support_express_checkout': True,
            'support_manual_capture': True,
            'support_refund': 'partial',
            'support_tokenization': True,
        })

    