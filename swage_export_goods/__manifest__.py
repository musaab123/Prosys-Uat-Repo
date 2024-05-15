{
    'name': "Swage Request Export Goods",
    'version': '16.0.1.2',
    'summary': """
        Apply Swage Request Export Goods.Easily access to Colloctor Payment and apply Swage Request Export Goods.User can easily  from portal.""",
    'description': """
        =>Apply Swage Request Export Goods.Easily access to stock and apply stock from portal.
        =>User can easily create expense from portals.
        =>Showninf old Colloctor Payment lines data.
    """,
    'category': 'Stock/ Request Export Goods',
    'author': 'Prosys',
    'company': 'PROSYS',
    'depends': ['base','stock','crm','sale','swage'],
    'data': [
        'reports/swage_request_goods.xml',
        'reports/conductor_header_footer.xml',
        'reports/report_view.xml',
        'views/views_goods.xml',
        'views/res_company.xml',


        


        
    ],

    'installable': True,
    'application': False,
    'auto_install': False,
}
