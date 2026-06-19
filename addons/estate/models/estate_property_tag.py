from odoo import fields, models

class EstatePropertyTag(models.Model):
    _name = "estate.property.tag"
    _description = "Estate Property Tag"

    active = fields.Boolean(default=True)
    name = fields.Char(required=True)

    _check_name = models.Constraint(
        'UNIQUE(name)',
        'The name must be unique.',
    )
