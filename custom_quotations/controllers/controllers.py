# -*- coding: utf-8 -*-
# from odoo import http


# class CustomQuotations(http.Controller):
#     @http.route('/custom_quotations/custom_quotations', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/custom_quotations/custom_quotations/objects', auth='public')
#     def list(self, **kw):
#         return http.request.render('custom_quotations.listing', {
#             'root': '/custom_quotations/custom_quotations',
#             'objects': http.request.env['custom_quotations.custom_quotations'].search([]),
#         })

#     @http.route('/custom_quotations/custom_quotations/objects/<model("custom_quotations.custom_quotations"):obj>', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('custom_quotations.object', {
#             'object': obj
#         })

