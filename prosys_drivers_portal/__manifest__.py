# -*- coding: utf-8 -*-

{
    'name': "Drivers Portal",
    'version': '16.0.1.2',
    'summary': """
        Drivers Portal
    """,
    'category': 'stock',
    'author': 'PROSYS',
    'company': 'PROSYS',
    'depends': ['prosys_driver_changes', 'portal'],
    'data': [
        'views/portal_product_templates_drivers.xml',
        
    ],
    'assets': {
        'web.assets_frontend': [
            '/prosys_drivers_portal/static/src/js/stock_portal.js',
            '/prosys_drivers_portal/static/src/js/picking_js.js',

        ],
    },
    'installable': True,
    'application': False,
    'auto_install': False,
}
