from odoo import models, fields, api

class HrContract(models.Model):
    _inherit = 'hr.contract'

    basic_salary = fields.Float(string="Basic Salary")
    home_rent = fields.Float(string="Home Rent")
    allowance = fields.Float(string="Allowance")

    # @api.depends('wage')
    # def _compute_salary_components(self):
    #     for contract in self:
    #         wage = contract.wage or 0.0
    #         contract.basic_salary = wage * 0.60
    #         contract.home_rent = wage * 0.30
    #         contract.allowance = wage * 0.10
