# Part of Odoo. See LICENSE file for full copyright and licensing details.

import base64

from odoo import fields, models

from odoo.addons.payment.logging import get_payment_logger
from odoo.addons.payment_midtrans import const


_logger = get_payment_logger(__name__)


class PaymentProvider(models.Model):
    _inherit = 'payment.provider'

    code = fields.Selection(
        selection_add=[('midtrans', "Midtrans")], ondelete={'midtrans': 'set default'}
    )
    midtrans_server_key = fields.Char(
        string="Midtrans Server Key",
        required_if_provider='midtrans',
        copy=False,
        groups='base.group_system',
    )
    midtrans_client_key = fields.Char(
        string="Midtrans Client Key",
        required_if_provider='midtrans',
        copy=False,
        groups='base.group_system',
    )

    # === COMPUTE METHODS === #

    def _compute_feature_support_fields(self):
        """ Override of `payment` to enable additional features. """
        super()._compute_feature_support_fields()
        # Midtrans Snap uses redirect flow only, no tokenization.
        self.filtered(lambda p: p.code == 'midtrans').update({
            'support_tokenization': False,
        })

    def _get_supported_currencies(self):
        """ Override of `payment` to return the supported currencies. """
        supported_currencies = super()._get_supported_currencies()
        if self.code == 'midtrans':
            supported_currencies = supported_currencies.filtered(
                lambda c: c.name in const.SUPPORTED_CURRENCIES
            )
        return supported_currencies

    # === CRUD METHODS === #

    def _get_default_payment_method_codes(self):
        """ Override of `payment` to return the default payment method codes. """
        self.ensure_one()
        if self.code != 'midtrans':
            return super()._get_default_payment_method_codes()
        return const.DEFAULT_PAYMENT_METHOD_CODES

    # === BUSINESS METHODS === #

    def _midtrans_get_api_url(self):
        """ Return the Midtrans API base URL based on the provider state.

        :return: The API base URL.
        :rtype: str
        """
        self.ensure_one()
        if self.state == 'test':
            return const.API_URLS['sandbox']
        return const.API_URLS['production']

    def _midtrans_get_auth_header(self):
        """ Build the Basic Auth header for Midtrans API requests.

        Midtrans uses Basic Auth with the Server Key as username and empty password.
        The header value is: Basic base64(server_key + ':')

        :return: The authorization headers dict.
        :rtype: dict
        """
        self.ensure_one()
        credentials = base64.b64encode(
            f"{self.midtrans_server_key}:".encode()
        ).decode()
        return {
            'Authorization': f'Basic {credentials}',
            'Content-Type': 'application/json',
            'Accept': 'application/json',
        }
