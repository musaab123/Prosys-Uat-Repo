# -*- coding: utf-8 -*-


{
    'name': 'Prosys Driver changes',
    'version': '16.0.1.0.0',
    'category': 'stock',
    'description': 'Driver changes.',
    'summary': 'Driver changes.',
    'author': 'PROSYS',
    'company': 'PROSYS',
    'maintainer': 'Prosys ',
    'depends': ['stock','base','sale_stock'],
    'data': [
        'security/ir.model.access.csv',
        'wizard/assign_driver.xml',
        'views/partner_view.xml',
        'views/picking.xml',
        'views/moves_view.xml',
    ],
    'installable': True,
    'application': False,
}

