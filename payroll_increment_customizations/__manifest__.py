# -*- coding: utf-8 -*-
{
    'name': "Payroll Increment",
    'author': "My Company",
    'category': 'Uncategorized',
    'version': '0.1',
    'depends': ['base', 'hr_payroll', 'hr_work_entry_contract_enterprise'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'views/hr_yearly_increment_views.xml',
        'data/increment_component.xml',
        # 'views/hr_payslip.xml',
        'views/hr_contract_views.xml',
    ],
    # only loaded in demonstration mode
    # 'demo': [
    #     'demo/demo.xml',
    # ],
}

