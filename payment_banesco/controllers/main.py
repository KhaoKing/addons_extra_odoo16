import hmac
import logging
import pprint

from werkzeug.exceptions import Forbidden
from odoo import http
from odoo.http import request

_logger = logging.getLogger(__name__)

class BanescoController(http.Controller):
    _banesco_return_url = '/payment/banesco/return' #Ruta para la redireccion de datos, que es enviada por Banesco.
    
    @http.route(_banesco_return_url, type='http', auth='public', csrf=False)
    def banesco_return_from_checkout(self, **data):
        _logger.info("handling redirection from Banesco with data:\n%s", pprint.pformat(data))  
        # Check the integrity of the notification
        tx_sudo = request.env['payment.transaction'].sudo()._get_tx_from_notification_data(
            'banesco', data
        )
        tx_sudo._handle_notification_data('banesco', data)
        return request.redirect('/payment/status')
    
