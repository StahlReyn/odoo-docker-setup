from odoo import fields, models, api

class EstatePropertyType(models.Model):
    _name = "estate.property.type"
    _description = "Estate Property Type"
    _order = "sequence, name"

    active = fields.Boolean(default=True)
    name = fields.Char(required=True)
    property_ids = fields.One2many("estate.property", "property_type_id", string="Properties")
    sequence = fields.Integer('Sequence', default=1, help="Used to order stages. Lower is better.")
    offer_ids = fields.One2many("estate.property.offer", "property_type_id", string="Offers")
    offer_count = fields.Integer(compute="_compute_offer_count")

    _check_name = models.Constraint(
        'UNIQUE(name)',
        'The name must be unique.',
    )

    @api.depends('offer_ids')
    def _compute_offer_count(self):
        for line in self:
            line.offer_count = len(line.offer_ids)