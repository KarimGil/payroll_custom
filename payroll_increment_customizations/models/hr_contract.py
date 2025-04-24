from odoo import models, fields, api

class HrContract(models.Model):
    _inherit = 'hr.contract'

    basic_salary = fields.Float(string="Basic Salary")
    hra = fields.Float(string="Home Rent")
    transport = fields.Float(string="Transportation Allowance")
    fuel = fields.Float(string="Fuel Allowance")


