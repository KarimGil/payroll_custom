from odoo import models, fields, api


class HrPayslip(models.Model):
    _inherit = 'hr.payslip'

    increment_amount = fields.Float('Increment Amount')
    # increment_amount_basic = fields.Float(string="Increment Amount B", readonly=True)
    # increment_amount_hra = fields.Float(string="Increment Amount H", readonly=True)
    # increment_amount_transport = fields.Float(string="Increment Amount T", readonly=True)
    # increment_amount_fuel = fields.Float(string="Increment Amount F", readonly=True)

    bp_qty = fields.Float('BP Qty', readonly=True)

    def _compute_updated_basic_salary(self):
        for slip in self:
            contract = slip.contract_id
            contract_amount = {'basic': contract.basic_salary, 'hra': contract.hra, 'transport': contract.transport, 'fuel': contract.fuel}

            if slip.struct_id:
                increment = self.env['hr.yearly.increment'].search([
                    ('structure_ids', 'in', slip.struct_id.id),
                    ('start_date', '<=', slip.date_from),
                    ('end_date', '>=', slip.date_to),
                ], limit=1)

                if increment:
                    components = {

                        'basic': increment.basic_increment,
                        'hra': increment.hra_increment,
                        'transport': increment.transport_increment,
                        'fuel': increment.fuel_increment,
                    }
                    for component in increment.increment_component_ids:

                        # Calculate the increment on basic salary
                        increment_amt = contract_amount[component.code] * components[component.code]  / 100.0
                        new_amount = contract_amount[component.code] + increment_amt

                        # Store the increment amount in the payslip
                        slip.increment_amount = increment_amt

                        # Apply the increment temporarily to contract
                        if component.code == 'basic':
                            contract.basic_salary = new_amount
                        elif component.code == 'hra':
                            contract.hra = new_amount
                        elif component.code == 'transport':
                            contract.transport = new_amount
                        else:
                            contract.fuel = new_amount

                        contract.wage = contract.basic_salary + contract.hra + contract.transport + contract.fuel

                        # Find the BP salary rule and set its amount to 500
                        bp_rule = self.env['hr.salary.rule'].search([
                            ('code', '=', f'BP_{component.code}'),
                            ('struct_id', '=', slip.struct_id.id)
                        ], limit=1)

                        if bp_rule:
                            if increment.back_p > 0:
                                bp_rule.write({
                                    'amount_fix': increment_amt,  # Set the amount to a fixed value (500)
                                })

                            else:
                                bp_rule.quantity = 0
                                bp_rule.amount_fix = 0
                    increment.back_p = 0

    def compute_sheet(self):
        for slip in self:
            slip._compute_updated_basic_salary()

            # Temporarily override contract wage
            contract = slip.contract_id
            if contract:
                original_wage = contract.wage
                try:
                    # Set contract wage to the updated wage based on basic salary
                    contract.wage = contract.basic_salary + contract.hra + contract.transport + contract.fuel
                    super(HrPayslip, slip).compute_sheet()
                finally:
                    # Restore original wage to avoid any permanent change
                    contract.wage = original_wage
            else:
                super(HrPayslip, slip).compute_sheet()
