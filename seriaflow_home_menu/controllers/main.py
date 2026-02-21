# -*- coding: utf-8 -*-
from odoo import http
from odoo.http import request
from odoo.addons.web.controllers.home import Home
from odoo.addons.web.controllers.utils import is_user_internal

class SeriaflowHome(Home):
    
    @http.route('/', type='http', auth="none")
    def index(self, s_action=None, db=None, **kw):
        """ Redirect the root domain directly to our custom Home Menu path """
        if request.db and request.session.uid and not is_user_internal(request.session.uid):
            return request.redirect_query('/web/login_successful', query=request.params)
        return request.redirect_query('/odoo/home', query=request.params)

    def _login_redirect(self, uid, redirect=None):
        """ Override the post-login redirect to push users to /odoo/home """
        url = super()._login_redirect(uid, redirect=redirect)
        if url == '/odoo':
            return '/odoo/home'
        return url
