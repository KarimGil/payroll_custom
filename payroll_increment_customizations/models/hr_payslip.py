from odoo import models, fields, api


class HrPayslip(models.Model):
    _inherit = 'hr.payslip'

    increment_amount = fields.Float(string="Increment Amount", readonly=True)
    bp_qty = fields.Float('BP Qty', readonly=True)

    def _compute_updated_basic_salary(self):
        for slip in self:
            contract = slip.contract_id
            basic_salary = contract.basic_salary  # Assuming this field exists on the contract

            if slip.struct_id:
                increment = self.env['hr.yearly.increment'].search([
                    ('structure_ids', 'in', slip.struct_id.id),
                    ('start_date', '<=', slip.date_from),
                    ('end_date', '>=', slip.date_to),
                ], limit=1)

                if increment:
                    # Calculate the increment on basic salary
                    increment_amt = basic_salary * increment.increment_percentage / 100.0
                    new_basic_salary = basic_salary + increment_amt

                    # Store the increment amount in the payslip
                    slip.increment_amount = increment_amt

                    # Apply the increment temporarily to contract
                    contract.basic_salary = new_basic_salary
                    contract.wage = new_basic_salary + contract.home_rent + contract.allowance

                    # Find the BP salary rule and set its amount to 500
                    bp_rule = self.env['hr.salary.rule'].search([
                        ('code', '=', 'BP'),
                        ('struct_id', '=', slip.struct_id.id)
                    ], limit=1)

                    if bp_rule:
                        if increment.back_p > 0:
                            bp_rule.write({
                                'amount_fix': increment_amt,  # Set the amount to a fixed value (500)
                            })
                            increment.back_p = 0
                        else:
                            bp_rule.quantity = 0
                            bp_rule.amount_fix = 0


    def compute_sheet(self):
        for slip in self:
            slip._compute_updated_basic_salary()

            # Temporarily override contract wage
            contract = slip.contract_id
            if contract:
                original_wage = contract.wage
                try:
                    # Set contract wage to the updated wage based on basic salary
                    contract.wage = contract.basic_salary + contract.home_rent + contract.allowance
                    super(HrPayslip, slip).compute_sheet()
                finally:
                    # Restore original wage to avoid any permanent change
                    contract.wage = original_wage
            else:
                super(HrPayslip, slip).compute_sheet()
