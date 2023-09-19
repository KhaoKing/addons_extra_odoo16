import hmac
import logging
import pprint
import json

from werkzeug.exceptions import Forbidden
from odoo import http
from odoo.http import request

_logger = logging.getLogger(__name__)

class BanescoController(http.Controller):
    _return_url = '/payment/banesco/return' #Ruta para la redireccion de datos, que es enviada por Banesco.

    @http.route(_return_url, type='json', auth='public', csrf=False)
    def banesco_return_from_checkout(self, **data):
        data = request.dispatcher.jsonrequest
        _logger.info("handling redirection from banesco with data:\n%s", pprint.pformat(data))
        if data:  # The customer has canceled or paid then clicked on "Return to Merchant"
            tx_sudo = request.env['payment.transaction'].sudo()._get_tx_from_notification_data(
                'banesco', data
            )
            tx_sudo._handle_notification_data('banesco', data)
        return request.redirect('/payment/status')
