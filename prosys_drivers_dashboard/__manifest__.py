{
    'name': "Drivers Dashboard",
    'version': '16.0.1.0.1',
    'summary': """Drivers Dashboard""",
    'description': """Drivers Dashboard""",
    'category': 'stock',
    'author': 'PROSYS',
    'company': 'PROSYS',
    'depends': ['stock','sale','base'],
    'data': [
        'security/ir.model.access.csv',
        'views/dashboard_views.xml',
    ],
    'assets': {
        'web.assets_backend': [
            'prosys_drivers_dashboard/static/src/css/drivers_dashboard.css',
            'prosys_drivers_dashboard/static/src/css/lib/nv.d3.css',
            'prosys_drivers_dashboard/static/src/js/drivers_dashboard.js',
            'prosys_drivers_dashboard/static/src/js/lib/d3.min.js',
            'prosys_drivers_dashboard/static/src/xml/drivers_dashboard.xml',
        ],
    },

    'images': ["static/description/banner.png"],
    'license': "AGPL-3",
    'installable': True,
    'application': True,
}
