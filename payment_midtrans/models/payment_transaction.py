# Part of Odoo. See LICENSE file for full copyright and licensing details.

import hashlib
import requests

from odoo import _, api, models
from odoo.exceptions import ValidationError
from odoo.tools import float_round

from odoo.addons.payment.logging import get_payment_logger
from odoo.addons.payment_midtrans import const
from odoo.addons.payment_midtrans.controllers.main import MidtransController


_logger = get_payment_logger(__name__)


class PaymentTransaction(models.Model):
    _inherit = 'payment.transaction'

    def _get_specific_rendering_values(self, processing_values):
        """ Override of `payment` to return Midtrans-specific rendering values.

        Note: self.ensure_one() from `_get_processing_values`

        :param dict processing_values: The generic and specific processing values of the transaction
        :return: The dict of provider-specific processing values.
        :rtype: dict
        """
        res = super()._get_specific_rendering_values(processing_values)
        if self.provider_code != 'midtrans':
            return res

        # Build the Snap API request payload.
        payload = self._midtrans_prepare_transaction_payload()

        # Call Midtrans Snap API to create a transaction and get the redirect URL.
        api_url = self.provider_id._midtrans_get_api_url()
        headers = self.provider_id._midtrans_get_auth_header()
        snap_url = f"{api_url}/snap/v1/transactions"

        try:
            response = requests.post(snap_url, json=payload, headers=headers, timeout=30)
            response.raise_for_status()
            snap_data = response.json()
        except requests.exceptions.RequestException as error:
            _logger.warning(
                "Midtrans Snap API request failed for transaction %s: %s",
                self.reference, error,
            )
            self._set_error(_(
                "Unable to create the Midtrans payment. Please try again later."
            ))
            return {}

        # Check for API errors in the response.
        if 'error_messages' in snap_data:
            error_msg = ', '.join(snap_data['error_messages'])
            _logger.warning(
                "Midtrans returned errors for transaction %s: %s",
                self.reference, error_msg,
            )
            self._set_error(_(
                "Midtrans returned an error: %(error)s", error=error_msg,
            ))
            return {}

        redirect_url = snap_data.get('redirect_url')
        if not redirect_url:
            _logger.warning(
                "Midtrans did not return a redirect URL for transaction %s. Response: %s",
                self.reference, snap_data,
            )
            self._set_error(_(
                "Unable to get the Midtrans payment page. Please try again later."
            ))
            return {}

        # Return the redirect URL for the form template.
        return {
            'api_url': redirect_url,
        }

    def _midtrans_prepare_transaction_payload(self):
        """ Create the payload for the Midtrans Snap transaction request.

        :return: The request payload.
        :rtype: dict
        """
        rounded_amount = int(float_round(
            self.amount, const.CURRENCY_DECIMALS.get('IDR', 0), rounding_method='DOWN'
        ))

        payload = {
            'transaction_details': {
                'order_id': self.reference,
                'gross_amount': rounded_amount,
            },
            'credit_card': {
                'secure': True,
            },
        }

        # Customer details.
        customer_details = {}
        if self.partner_name:
            names = self.partner_name.split(' ', 1)
            customer_details['first_name'] = names[0]
            if len(names) > 1:
                customer_details['last_name'] = names[1]
        if self.partner_email:
            customer_details['email'] = self.partner_email
        if self.partner_id.phone:
            customer_details['phone'] = self.partner_id.phone

        # Billing address.
        billing_address = {}
        if self.partner_name:
            names = self.partner_name.split(' ', 1)
            billing_address['first_name'] = names[0]
            if len(names) > 1:
                billing_address['last_name'] = names[1]
        if self.partner_email:
            billing_address['email'] = self.partner_email
        if self.partner_id.phone:
            billing_address['phone'] = self.partner_id.phone
        if self.partner_address:
            billing_address['address'] = self.partner_address
        if self.partner_city:
            billing_address['city'] = self.partner_city
        if self.partner_zip:
            billing_address['postal_code'] = self.partner_zip
        if self.partner_country_id.code:
            billing_address['country_code'] = self.partner_country_id.code

        if billing_address:
            customer_details['billing_address'] = billing_address
        if customer_details:
            payload['customer_details'] = customer_details

        return payload

    @api.model
    def _extract_reference(self, provider_code, payment_data):
        """ Override of `payment` to extract the reference from the payment data. """
        if provider_code != 'midtrans':
            return super()._extract_reference(provider_code, payment_data)
        return payment_data.get('order_id')

    def _extract_amount_data(self, payment_data):
        """ Override of payment to extract the amount and currency from the payment data. """
        if self.provider_code != 'midtrans':
            return super()._extract_amount_data(payment_data)

        amount = payment_data.get('gross_amount', '0')
        return {
            'amount': float(amount),
            'currency_code': payment_data.get('currency', 'IDR'),
            'precision_digits': const.CURRENCY_DECIMALS.get('IDR'),
        }

    def _apply_updates(self, payment_data):
        """ Override of `payment` to update the transaction based on the payment data. """
        if self.provider_code != 'midtrans':
            return super()._apply_updates(payment_data)

        # Update the provider reference.
        self.provider_reference = payment_data.get('transaction_id')

        # Update the payment state based on Midtrans transaction_status.
        payment_status = payment_data.get('transaction_status', '')
        fraud_status = payment_data.get('fraud_status', '')

        # For credit card with capture status, also check fraud_status.
        if payment_status == 'capture':
            if fraud_status == 'accept':
                self._set_done()
            elif fraud_status == 'challenge':
                self._set_pending()
            else:
                self._set_error(_(
                    "The payment was flagged as potentially fraudulent."
                ))
        elif payment_status in const.PAYMENT_STATUS_MAPPING['pending']:
            self._set_pending()
        elif payment_status in const.PAYMENT_STATUS_MAPPING['done']:
            self._set_done()
        elif payment_status in const.PAYMENT_STATUS_MAPPING['cancel']:
            self._set_canceled()
        elif payment_status in const.PAYMENT_STATUS_MAPPING['error']:
            status_message = payment_data.get('status_message', '')
            self._set_error(_(
                "An error occurred during the processing of your payment: %(msg)s",
                msg=status_message,
            ))
