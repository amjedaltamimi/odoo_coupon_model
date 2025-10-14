# custom_quotations/__manifest__.py
{
    'name': 'Custom Quotation Templates & Coupons',
    'version': '1.0',
    "sequence": "2",
    'summary': 'Create quotations from templates and manage discount coupons.',
    'author': 'amjed altamimi',
    'depends': ['sale_management'],
    'data': [

        'security/ir.model.access.csv',
        'views/menu.xml',
        'views/coupon_views.xml',
        'views/quotation_template_views.xml',
        'views/sale_order_views.xml',
    ],
    'installable': True,
    'application': True,
}
