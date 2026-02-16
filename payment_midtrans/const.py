# Part of Odoo. See LICENSE file for full copyright and licensing details.

# The currencies supported by Midtrans, in ISO 4217 format.
# Midtrans primarily supports IDR transactions.
SUPPORTED_CURRENCIES = [
    'IDR',
]

# To correctly allow lowest decimal place rounding.
CURRENCY_DECIMALS = {
    'IDR': 0,
}

# The codes of the payment methods to activate when Midtrans is activated.
DEFAULT_PAYMENT_METHOD_CODES = {
    # Primary payment methods.
    'card',
    'gopay',
    'shopeepay',
    'qris',

    # Brand payment methods.
    'visa',
    'mastercard',
}

# Midtrans API base URLs.
API_URLS = {
    'sandbox': 'https://app.sandbox.midtrans.com',
    'production': 'https://app.midtrans.com',
}

# Mapping of transaction states to Midtrans payment statuses.
# https://docs.midtrans.com/docs/transaction-status-cycle
PAYMENT_STATUS_MAPPING = {
    'draft': (),
    'pending': ('pending',),
    'done': ('capture', 'settlement'),
    'cancel': ('cancel', 'deny', 'expire'),
    'error': ('failure',),
}
