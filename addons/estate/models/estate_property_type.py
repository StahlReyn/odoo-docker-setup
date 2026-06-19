from odoo import fields, models

class EstatePropertyType(models.Model):
    _name = "estate.property.type"
    _description = "Estate Property Type"

    active = fields.Boolean(default=True)
    name = fields.Char(required=True)
    description = fields.Text()