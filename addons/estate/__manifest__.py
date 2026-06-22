{
    'name': "Real Estate",
    'version': '19.0.0.0.0',
    'depends': ['base'],
    'author': "Odoo Community Association (OCA), John Estate",
    'category': 'Estate',
    'license': "LGPL-3",
    'application': True,
    'data': [
        'security/ir.model.access.csv',
        'views/estate_property_views.xml',
        'views/estate_property_offer_views.xml',
        'views/estate_property_type_views.xml',
        'views/estate_property_tag_views.xml',
        'views/estate_property_menus.xml',
        'views/res_users_views.xml',
    ],
} # pyright: ignore[reportUnusedExpression]