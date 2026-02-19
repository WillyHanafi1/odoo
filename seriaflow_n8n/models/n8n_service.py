import requests
import json
import logging
from odoo import models, api

_logger = logging.getLogger('seriaflow.n8n')

class N8nService(models.AbstractModel):
    _name = 'seriaflow.n8n.service'
    _description = 'n8n Integration Service'

    @api.model
    def post_webhook(self, url, data):
        """
        Send a POST request to n8n webhook safely from Automated Actions.
        """
        headers = {'Content-Type': 'application/json'}
        try:
            response = requests.post(url, json=data, headers=headers, timeout=5)
            response.raise_for_status()
            _logger.info("n8n Webhook Success: %s", url)
            return True
        except Exception as e:
            _logger.error("n8n Webhook Failed: %s. Error: %s", url, str(e))
            # Log error to Odoo system logs so user can see it in Technical > Logging
            self.env['ir.logging'].sudo().create({
                'name': 'n8n Webhook Error',
                'type': 'server',
                'level': 'error',
                'message': f"Failed to send to {url}: {str(e)}",
                'path': 'seriaflow.n8n.service',
                'func': 'post_webhook',
                'line': '0',
            })
            return False
