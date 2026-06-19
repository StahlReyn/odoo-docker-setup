from odoo import fields, models

class EstatePropertyType(models.Model):
    _name = "estate.property.type"
    _description = "Estate Property Type"

    active = fields.Boolean(default=True)
    name = fields.Char(required=True)

    _check_name = models.Constraint(
        'UNIQUE(name)',
        'The name must be unique.',
    )