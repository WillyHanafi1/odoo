{
    'name': 'Seriaflow n8n Integration',
    'version': '1.0',
    'summary': 'Helper module to send webhooks to n8n from Automated Actions',
    'description': """
        This module provides a safe method to send webhooks to n8n,
        bypassing Odoo's Safe Eval restrictions in Automated Actions.
        
        Usage in Automated Action:
        env['seriaflow.n8n.service'].post_webhook('https://n8n.yoursite.com/...', payload_dict)
    """,
    'author': 'Seriaflow',
    'category': 'Technical',
    'depends': ['base'],
    'data': [],
    'installable': True,
    'application': False,
    'license': 'LGPL-3',
}
