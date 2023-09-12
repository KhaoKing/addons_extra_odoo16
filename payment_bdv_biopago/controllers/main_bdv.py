import hashlib
import hmac
import json
import logging
import pprint
from datetime import datetime
import werkzeug
from werkzeug import urls
from werkzeug.exceptions import Forbidden

from odoo import http
from odoo.exceptions import ValidationError
from odoo.http import request
from odoo.tools.misc import file_open

from odoo.addons.payment import utils as payment_utils
from odoo.addons.payment_bdv_biopago import utils as bdv_utils


_logger = logging.getLogger(__name__)

res_code = {
    0:'Pendiente',
    1:'Procesado',
    2:'En Proceso',
    3:'Cancelado',
}

class VenezuelaPaymentsControllers(http.Controller):
    _checkout_return_url = '/payment/venezuerla/redirect'
    _validation_return_url = '/payment/stripe/validation_return'
    @http.route(_checkout_return_url, type='http', auth='public', csrf=False)
    def stripe_return_from_checkout(self, **data):
        """ Process the notification data sent by Stripe after redirection from checkout.

        :param dict data: The GET params appended to the URL in `_stripe_create_checkout_session`
        """
        # Retrieve the tx based on the tx reference included in the return url
        tx_sudo = request.env['payment.transaction'].sudo()._get_tx_from_notification_data(
            'stripe', data
        )

        tx_sudo._handle_notification_data('stripe', data)
    
    # @http.route(
    #     '/shop/payment/transaction/<int:order_id>', type='json', auth='public', website=True
    # )
    # def shop_payment_transaction(self, order_id, access_token, **kwargs):
    #     print ('hola mundooooo')
    #     print ('hola mundooooo')
    #     print ('hola mundooooo')
    #     print ('hola mundooooo')
    #     print (kwargs)
    #     url = request.env['payment.provider'].browse([kwargs.get('payment_option_id')]).bdv_url_token
    #     print (access_token)
    #     # url = kwargs.get('x_relay_url',False)
    #     print (url)
    #     if url:
    #         print ("Holaa")
    #         print ("Holaa")
    #         print ("Holaa")
    #         print ("Holaa")
    #         print ("Holaa")
    #         return request.redirect(url)
    #     else:
    #         raise werkzeug.exceptions.NotFound()
        