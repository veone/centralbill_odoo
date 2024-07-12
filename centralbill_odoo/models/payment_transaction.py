# Part of Odoo. See LICENSE file for full copyright and licensing details.

import logging

import datetime
from datetime import datetime
import logging
import time
import pytz

from werkzeug import urls

from odoo import _, api, models
from odoo.exceptions import ValidationError

from ..const import STATUS_CODES_MAPPING
from ..controllers.main import CentralbillController

_logger = logging.getLogger(__name__)


class PaymentTransaction(models.Model):
    _inherit = 'payment.transaction'

    def _get_specific_rendering_values(self, processing_values):
        """ Override of payment to return Centralbill-specific rendering values.

        Note: self.ensure_one() from `_get_processing_values`

        :param dict processing_values: The generic and specific processing values of the transaction
        :return: The dict of provider-specific processing values
        :rtype: dict
        """
        res = super()._get_specific_rendering_values(processing_values)
        if self.provider_code != 'centralbill':
            return res
        
        today_utc = pytz.UTC.localize(datetime.utcnow())
        today_iso = today_utc.isoformat('T', 'seconds')
        
        redirect_url = urls.url_join(self.provider_id.get_base_url(), CentralbillController._redirect_url)
        webhook_url = urls.url_join(self.provider_id.get_base_url(), CentralbillController._webhook_url)
        
        https_redirect_url = redirect_url
        if redirect_url.startswith("http://"):
            https_redirect_url = redirect_url.replace("http://", "https://")
            
        https_webhook_url = webhook_url
        if webhook_url.startswith("http://"):
            https_webhook_url = webhook_url.replace("http://", "https://")

        rendering_values = {
            'acquirer': self.provider_id.id,
            'item_number': self.reference,
            'application_name': self.provider_id.centralbill_app_name,
            'application_id': self.provider_id.centralbill_app_key,
            'secret': self.provider_id.centralbill_secret_key,
            'invoice_id': self.reference,
            'customer_id': self.partner_id.id,
            'issued_at': today_iso,
            'due_date': today_iso,
            'total_amount_amount': int(self.amount),
            'total_amount_currency': self.currency_id.name,
            'description': self.reference,
            "callback_url": https_webhook_url,
            "api_url": self.provider_id._centralbill_get_api_url(),
            "redirect_url": https_redirect_url,   
        }
        rendering_values['signature'] = self.provider_id._centralbill_generate_digital_sign(rendering_values, incoming=False)
        return rendering_values

    def _get_tx_from_notification_data(self, provider_code, notification_data):
        """ Override of payment to find the transaction based on Centralbill data.

        :param str provider_code: The code of the provider that handled the transaction
        :param dict notification_data: The normalized notification data sent by the provider
        :return: The transaction if found
        :rtype: recordset of `payment.transaction`
        :raise: ValidationError if the data match no transaction
        """
        tx = super()._get_tx_from_notification_data(provider_code, notification_data)
        if provider_code != 'centralbill' or len(tx) == 1:
            return tx

        reference = notification_data.get('invoice')
        tx = self.search([('reference', '=', reference.get('id')), ('provider_code', '=', 'centralbill')])
        
        print("BEGIN CONTAINED OF REFERENCE")
        print(reference)
        print("END CONTAINED OF REFERENCE")
        
        if not tx:
            print("BEGIN CONTAINED OF REFERENCE")
            print(reference)
            print("END CONTAINED OF REFERENCE")
            raise ValidationError("Centralbill: " + _("No transaction found matching reference %s.", reference))
        return tx

    def _process_notification_data(self, notification_data):
        """ Override of payment to process the transaction based on Centralbill data.

        Note: self.ensure_one()

        :param dict notification_data: The normalized notification data sent by the provider
        :return: None
        :raise: ValidationError if inconsistent data were received
        """
        super()._process_notification_data(notification_data)
        if self.provider_code != 'centralbill':
            return
        
        transaction_keys = notification_data.get('externaltransactionid')
        if not transaction_keys:
            raise ValidationError("Centralbill: " + _("Received data with missing transaction keys"))
        
        self.provider_reference = transaction_keys
        status_code = notification_data.get('result').get('status')
        if status_code in STATUS_CODES_MAPPING['pending']:
            self._set_pending()
        elif status_code in STATUS_CODES_MAPPING['done']:
            self._set_done()
        elif status_code in STATUS_CODES_MAPPING['cancel']:
            self._set_canceled()
        elif status_code in STATUS_CODES_MAPPING['refused']:
            self._set_error(_("Your payment was refused (code %s). Please try again.", status_code))
        elif status_code in STATUS_CODES_MAPPING['error']:
            self._set_error(_("An error occurred during processing of your payment (code %s). Please try again.", status_code))
        else:
            _logger.warning("received data with invalid payment status (%s) for transaction with reference %s", status_code, self.reference)
            self._set_error("Centralbill: " + _("Unknown status code: %s", status_code))
