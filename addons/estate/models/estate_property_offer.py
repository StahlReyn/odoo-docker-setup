from odoo import fields, models

class EstatePropertyOffer(models.Model):
    _name = "estate.property.offer"
    _description = "Estate Property Offer"

    active = fields.Boolean(default=True)
    price = fields.Float()
    status = fields.Selection(
        string='State',
        selection=[
            ('accepted', 'Accepted'), 
            ('refused', 'Refused')], # type: ignore
        help="Status of the offer",
        copy=False)
    partner_id = fields.Many2one('res.partner', string='Partner', required=True)
    property_id = fields.Many2one('estate.property', string='Property', required=True)