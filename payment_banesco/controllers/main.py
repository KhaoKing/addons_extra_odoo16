import hmac
import logging
import pprint

from werkzeug.exceptions import Forbidden
from odoo import http
from odoo.http import request

_logger = logging.getLogger(__name__)

class StripeController(http.Controller):
    _banesco_return_url = '/payment/banesco/return'


    @http.route(_banesco_return_url, type='http', auth='public', csrf=False)
    def banesco_return_from_checkout(self, **data):
        _logger.info("handling redirection from Banesco with data:\n%s", pprint.pformat(data))

        # Check the integrity of the notification
        tx_sudo = request.env['payment.transaction'].sudo()._get_tx_from_notification_data(
            'banesco', data
        )
        self._verify_notification_signature(data, tx_sudo)

        # Handle the notification data
        # tx_sudo._handle_notification_data('alipay', data)
        return request.redirect('/payment/status')
    


    @staticmethod
    def _verify_notification_signature(notification_data, tx_sudo):
        """ Check that the received signature matches the expected one.

        :param dict notification_data: The notification data
        :param recordset tx_sudo: The sudoed transaction referenced by the notification data, as a
                                  `payment.transaction` record
        :return: None
        :raise: :class:`werkzeug.exceptions.Forbidden` if the signatures don't match
        """
        # Retrieve the received signature from the data
        received_signature = notification_data.get('sign')
        if not received_signature:
            _logger.warning("received notification with missing signature")
            raise Forbidden()

        # Compare the received signature with the expected signature computed from the data
        expected_signature = tx_sudo.provider_id._alipay_compute_signature(notification_data)
        if not hmac.compare_digest(received_signature, expected_signature):
            _logger.warning("received notification with invalid signature")
            raise Forbidden()
