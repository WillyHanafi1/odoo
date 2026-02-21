# -*- coding: utf-8 -*-
from odoo import http
from odoo.http import request
from odoo.addons.web.controllers.home import Home
from odoo.addons.web.controllers.utils import is_user_internal

class SeriaflowHome(Home):
    
    @http.route()
    def index(self, *args, **kw):
        """ Redirect the root domain to our custom Home Menu path if logged in """
        if request.session.uid and is_user_internal(request.session.uid):
            return request.redirect_query('/odoo/home', query=request.params)
        return super().index(*args, **kw)

    def _login_redirect(self, uid, redirect=None):
        """ Override the post-login redirect to push users to /odoo/home """
        url = super()._login_redirect(uid, redirect=redirect)
        if url == '/odoo':
            return '/odoo/home'
        return url
