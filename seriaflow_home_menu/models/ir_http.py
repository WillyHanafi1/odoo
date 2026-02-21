# -*- coding: utf-8 -*-

import werkzeug

from odoo import models
from odoo.http import request


class IrHttp(models.AbstractModel):
    _inherit = 'ir.http'

    @classmethod
    def _post_dispatch(cls, response):
        response = super()._post_dispatch(response)
        
        # Intercept redirects to the default backend '/odoo' and override with our Home Menu
        if hasattr(response, 'location') and response.location:
            if request.session.uid and request.env.user._is_internal():
                # Strictly check if it's redirecting to the root backend (with or without query parameters)
                if response.location == '/odoo' or response.location.startswith('/odoo?'):
                    response.location = response.location.replace('/odoo', '/odoo/home', 1)
                    
        return response
