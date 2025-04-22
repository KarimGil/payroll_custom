from odoo import models, fields, api

class HrYearlyIncrement(models.Model):
    _name = 'hr.yearly.increment'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char(string="Name", required=True)
    start_date = fields.Date(string="Start Date", required=True)
    end_date = fields.Date(string="End Date", required=True)
    increment_percentage = fields.Float(string="Increment Percentage", required=True)
    structure_ids = fields.Many2many('hr.payroll.structure', string="Salary Structures")
    back_p = fields.Integer(string="Back Payments")
    state = fields.Selection([
        ('draft', 'Draft'),
        ('confirmed', 'Confirmed')
    ], string="Status", default='draft', tracking=True)

    def action_confirm_increment(self):
        for increment in self:
            if increment.back_p > 0:
                rule_obj = self.env['hr.salary.rule']
                category = self.env['hr.salary.rule.category'].search([('name', '=', 'Allowance')], limit=1)

                for structure in increment.structure_ids:
                    existing_rule = rule_obj.search([
                        ('code', '=', 'BP'),
                        ('struct_id', '=', structure.id)
                    ], limit=1)

                    rule_vals = {
                        'name': 'Back P',
                        'category_id': category.id,
                        'code': 'BP',
                        'sequence': 5,
                        'struct_id': structure.id,
                        'active': True,
                        'appears_on_payslip': True,
                        'quantity': increment.back_p,
                        'amount_select': 'code',
                        'amount_python_compute': 'result = contract.wage * 0',  # or your own logic
                    }

                    if existing_rule:
                        existing_rule.write({
                            'quantity': increment.back_p
                        })
                    else:
                        rule_obj.create(rule_vals)

            increment.state = 'confirmed'
