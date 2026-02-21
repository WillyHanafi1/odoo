# -*- coding: utf-8 -*-

import werkzeug

from odoo import models
from odoo.http import request


class IrHttp(models.AbstractModel):
    _inherit = 'ir.http'

    @classmethod
    def _pre_dispatch(cls, rule, args):
        super()._pre_dispatch(rule, args)

        # Only redirect logged-in internal users who visit '/' directly via a
        # top-level browser navigation (not iframes, assets, or fetch requests).
        # We detect top-level navigation using the Sec-Fetch-Dest header:
        #   - 'document' = real browser tab navigation ✅ redirect
        #   - 'iframe', 'embed', 'empty', etc. = Website Editor / AJAX ❌ skip
        if request.httprequest.path == '/':
            sec_fetch_dest = request.httprequest.headers.get('Sec-Fetch-Dest', '')
            if sec_fetch_dest == 'document':
                if request.session.uid and request.env.user._is_internal():
                    werkzeug.exceptions.abort(request.redirect('/odoo/home', code=302))

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
