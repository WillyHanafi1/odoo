# Part of Odoo. See LICENSE file for full copyright and licensing details.

{
    'name': "Payment Provider: Midtrans",
    'version': '1.0',
    'category': 'Accounting/Payment Providers',
    'sequence': 351,
    'summary': "A payment provider for Indonesia using Midtrans Snap.",
    'description': " ",  # Non-empty string to avoid loading the README file.
    'depends': ['payment'],
    'data': [
        'views/payment_midtrans_templates.xml',
        'views/payment_provider_views.xml',

        'data/payment_provider_data.xml',  # Depends on payment_midtrans_templates.xml
    ],
    'post_init_hook': 'post_init_hook',
    'uninstall_hook': 'uninstall_hook',
    'author': 'Seriaflow',
    'license': 'LGPL-3',
}
