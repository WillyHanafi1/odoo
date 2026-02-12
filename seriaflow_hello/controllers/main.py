from odoo import http
from odoo.http import request


class SeriaflowHello(http.Controller):

    @http.route('/hello', type='http', auth='public', website=True)
    def hello_page(self, **kwargs):
        return request.render('seriaflow_hello.hello_page', {})
