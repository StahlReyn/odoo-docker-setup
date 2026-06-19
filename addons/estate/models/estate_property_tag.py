from odoo import fields, models

class EstatePropertyTag(models.Model):
    _name = "estate.property.tag"
    _description = "Estate Property Tag"

    active = fields.Boolean(default=True)
    name = fields.Char(required=True)