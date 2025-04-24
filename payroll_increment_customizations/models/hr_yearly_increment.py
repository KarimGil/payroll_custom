from odoo import models, fields, api


class HrYearlyIncrement(models.Model):
    _name = 'hr.yearly.increment'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char(string="Name", required=True)
    start_date = fields.Date(string="Start Date", required=True)
    end_date = fields.Date(string="End Date", required=True)
    # increment_percentage = fields.Float(string="Increment Percentage", required=True)
    structure_ids = fields.Many2many('hr.payroll.structure', string="Salary Structures")

    back_p = fields.Integer(string="No of Occurrences", compute="_compute_occurrences", store=True)

    state = fields.Selection([
        ('draft', 'Draft'),
        ('confirmed', 'Confirmed')
    ], string="Status", default='draft', tracking=True)
    increment_component_ids = fields.Many2many(
        'hr.increment.component',
        string="Increment Components"
    )
    basic_increment = fields.Float(string="Increment for Basic Salary (%)")
    hra_increment = fields.Float(string="Increment for House Rent Allowance (%)")
    transport_increment = fields.Float(string="Increment for Transportation Allowance (%)")
    fuel_increment = fields.Float(string="Increment for Fuel Allowance (%)")

    # Computed fields to check selected components
    basic_selected = fields.Boolean(string="Is Basic Selected", compute="_compute_selected_components")
    hra_selected = fields.Boolean(string="Is HRA Selected", compute="_compute_selected_components")
    transport_selected = fields.Boolean(string="Is Transport Selected", compute="_compute_selected_components")
    fuel_selected = fields.Boolean(string="Is Fuel Selected", compute="_compute_selected_components")

    @api.depends('increment_component_ids')
    def _compute_selected_components(self):
        for rec in self:
            rec.basic_selected = any(component.code == 'basic' for component in rec.increment_component_ids)
            rec.hra_selected = any(component.code == 'hra' for component in rec.increment_component_ids)
            rec.transport_selected = any(component.code == 'transport' for component in rec.increment_component_ids)
            rec.fuel_selected = any(component.code == 'fuel' for component in rec.increment_component_ids)

    @api.depends('start_date')
    def _compute_occurrences(self):
        for rec in self:
            if rec.start_date:
                rec.back_p = rec.start_date.month - 1
            else:
                rec.back_p = 0

    def action_confirm_increment(self):
        for increment in self:
            if increment.back_p > 0:
                rule_obj = self.env['hr.salary.rule']
                category = self.env['hr.salary.rule.category'].search([('name', '=', 'Allowance')], limit=1)

                # Loop through each increment component selected by the user
                for component in increment.increment_component_ids:
                    # Determine the name of the salary rule based on the component
                    rule_name = f"Back P for {component.name}"
                    rule_code = f"BP_{component.code}"

                    # Search for an existing rule for this structure and component
                    for structure in increment.structure_ids:
                        existing_rule = rule_obj.search([
                            ('code', '=', rule_code),
                            ('struct_id', '=', structure.id)
                        ], limit=1)

                        rule_vals = {
                            'name': rule_name,
                            'category_id': category.id,
                            'code': rule_code,
                            'sequence': 5,
                            'struct_id': structure.id,
                            'active': True,
                            'appears_on_payslip': True,
                            'quantity': increment.back_p,
                            # 'amount_select': 'code',
                            # 'amount_python_compute': 'result = contract.wage * 0',  # Or your own logic
                        }

                        # Update or create the rule
                        if existing_rule:
                            existing_rule.write({
                                'quantity': increment.back_p
                            })
                        else:
                            rule_obj.create(rule_vals)

            # Change the state to 'confirmed'
            increment.state = 'confirmed'


class HrIncrementComponent(models.Model):
    _name = 'hr.increment.component'
    _description = "Increment Component"

    name = fields.Char(required=True)
    code = fields.Char(required=True)
