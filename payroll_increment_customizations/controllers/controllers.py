# -*- coding: utf-8 -*-
# from odoo import http


# class PayrollIncrementCustomizations(http.Controller):
#     @http.route('/payroll_increment_customizations/payroll_increment_customizations', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/payroll_increment_customizations/payroll_increment_customizations/objects', auth='public')
#     def list(self, **kw):
#         return http.request.render('payroll_increment_customizations.listing', {
#             'root': '/payroll_increment_customizations/payroll_increment_customizations',
#             'objects': http.request.env['payroll_increment_customizations.payroll_increment_customizations'].search([]),
#         })

#     @http.route('/payroll_increment_customizations/payroll_increment_customizations/objects/<model("payroll_increment_customizations.payroll_increment_customizations"):obj>', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('payroll_increment_customizations.object', {
#             'object': obj
#         })

