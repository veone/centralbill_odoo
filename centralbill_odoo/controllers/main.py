# Part of Odoo. See LICENSE file for full copyright and licensing details.

import hmac
import logging
import pprint

from werkzeug.exceptions import Forbidden

from odoo import http
from odoo.exceptions import ValidationError
from odoo.http import request

_logger = logging.getLogger(__name__)


class CentralbillController(http.Controller):
    _return_url = '/payment/centralbill/return'
    _webhook_url = '/payment/centralbill/webhook'
    _redirect_url = '/'
    _cancel_url = '/payment/centralbill/cancel'
    _notify_url = '/payment/centralbill'

    @http.route(_return_url, type='http', auth='public', methods=['POST'], csrf=False, save_session=False)
    def centralbill_return_from_checkout(self, **raw_data):
        """ Process the notification data sent by Centralbill after redirection from checkout.

        The route is flagged with `save_session=False` to prevent Odoo from assigning a new session
        to the user if they are redirected to this route with a POST request. Indeed, as the session
        cookie is created without a `SameSite` attribute, some browsers that don't implement the
        recommended default `SameSite=Lax` behavior will not include the cookie in the redirection
        request from the payment provider to Odoo. As the redirection to the '/payment/status' page
        will satisfy any specification of the `SameSite` attribute, the session of the user will be
        retrieved and with it the transaction which will be immediately post-processed.

        :param dict raw_data: The un-formatted notification data
        """

        event = request.get_json_data()
        data = self._normalize_data_keys(event)

        # Check the integrity of the notification
        tx_sudo = request.env['payment.transaction'].sudo()._get_tx_from_notification_data('centralbill', data)
        
        # Handle the notification data
        tx_sudo._handle_notification_data('centralbill', data)
        return request.redirect(self._redirect_url)
    
    @http.route(_webhook_url, type='http', auth='public', methods=['POST'], csrf=False)
    def centralbill_webhook(self):
        """ Process the notification data sent by Centralbill to the webhook.

        See https://www.pronamic.nl/wp-content/uploads/2013/04/BPE-3.0-Gateway-HTML.1.02.pdf.

        :param dict event: The un-formatted notification data
        :return: An empty string to acknowledge the notification
        :rtype: str
        """
        event = request.get_json_data()
        data = self._normalize_data_keys(event)
        try:
            
            # Check the integrity of the notification
            tx_sudo = request.env['payment.transaction'].sudo()._get_tx_from_notification_data('centralbill', data)

            # Handle the notification data
            tx_sudo._handle_notification_data('centralbill', data)
        except ValidationError:  # Acknowledge the notification to avoid getting spammed
            pass
        return ''

    @staticmethod
    def _normalize_data_keys(data):
        """ Set all keys of a dictionary to lower-case.

        As Centralbill parameters names are case insensitive, we can convert everything to lower-case
        to easily detected the presence of a parameter by checking the lower-case key only.

        :param dict data: The dictionary whose keys must be set to lower-case
        :return: A copy of the original data with all keys set to lower-case
        :rtype: dict
        """
        return {key.lower(): val for key, val in data.items()}

    @staticmethod
    def _verify_notification_signature(notification_data, received_signature, tx_sudo):
        """ Check that the received signature matches the expected one.

        :param dict notification_data: The notification data
        :param str received_signature: The signature received with the notification data
        :param recordset tx_sudo: The sudoed transaction referenced by the notification data, as a
                                  `payment.transaction` record
        :return: None
        :raise: :class:`werkzeug.exceptions.Forbidden` if the signatures don't match
        """
        # Check for the received signature
        if not received_signature:
            raise Forbidden()

        # Compare the received signature with the expected signature computed from the data
        expected_signature = tx_sudo.provider_id._centralbill_generate_digital_sign(
            notification_data, incoming=True
        )
        if not hmac.compare_digest(received_signature, expected_signature):
            raise Forbidden()