# Part of Odoo. See LICENSE file for full copyright and licensing details.

import hashlib
import pprint

from werkzeug.exceptions import Forbidden

from odoo import http
from odoo.http import request

from odoo.addons.payment.logging import get_payment_logger


_logger = get_payment_logger(__name__)


class MidtransController(http.Controller):

    _webhook_url = '/payment/midtrans/webhook'
    _return_url = '/payment/midtrans/return'

    @http.route(_webhook_url, type='http', methods=['POST'], auth='public', csrf=False)
    def midtrans_webhook(self):
        """ Process the payment notification sent by Midtrans.

        Midtrans sends HTTP POST notifications with JSON body containing the transaction status.
        We verify the signature key to ensure the notification is authentic.

        :return: An HTTP 200 response to acknowledge the notification.
        """
        data = request.get_json_data()
        _logger.info("Notification received from Midtrans with data:\n%s", pprint.pformat(data))

        # Find the transaction.
        tx_sudo = request.env['payment.transaction'].sudo()._search_by_reference(
            'midtrans', data
        )
        if not tx_sudo:
            _logger.warning("No transaction found for Midtrans notification: %s", data)
            return request.make_json_response({'status': 'ok'}, status=200)

        # Verify the signature key.
        self._verify_notification_signature(data, tx_sudo)

        # Process the notification.
        tx_sudo._process('midtrans', data)

        return request.make_json_response({'status': 'ok'}, status=200)

    @http.route(_return_url, type='http', methods=['GET'], auth='public')
    def midtrans_return(self, **data):
        """ Handle the return from Midtrans payment page.

        After payment, Midtrans redirects the customer back to this URL.
        We simply redirect to the Odoo payment status page.

        :return: A redirect to the payment status page.
        """
        return request.redirect('/payment/status')

    def _verify_notification_signature(self, data, tx_sudo):
        """ Verify the signature key from Midtrans notification.

        Midtrans signs notifications with a signature_key computed as:
        SHA512(order_id + status_code + gross_amount + server_key)

        :param dict data: The notification data from Midtrans.
        :param payment.transaction tx_sudo: The transaction referenced by the notification.
        :return: None
        :raise Forbidden: If the signature verification fails.
        """
        received_signature = data.get('signature_key', '')
        if not received_signature:
            _logger.warning("Received Midtrans notification without signature key.")
            raise Forbidden()

        order_id = data.get('order_id', '')
        status_code = data.get('status_code', '')
        gross_amount = data.get('gross_amount', '')
        server_key = tx_sudo.provider_id.midtrans_server_key

        # Compute the expected signature: SHA512(order_id + status_code + gross_amount + server_key)
        raw_signature = f"{order_id}{status_code}{gross_amount}{server_key}"
        expected_signature = hashlib.sha512(raw_signature.encode()).hexdigest()

        if received_signature != expected_signature:
            _logger.warning(
                "Received Midtrans notification with invalid signature for transaction %s.",
                order_id,
            )
            raise Forbidden()
