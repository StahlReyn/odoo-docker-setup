from odoo import fields, models, api
from dateutil.relativedelta import relativedelta

class EstatePropertyOffer(models.Model):
    _name = "estate.property.offer"
    _description = "Estate Property Offer"
    _order = "price desc"

    active = fields.Boolean(default=True)
    price = fields.Float()
    status = fields.Selection(
        string='State',
        selection=[
            ('accepted', 'Accepted'), 
            ('refused', 'Refused')], # type: ignore
        help="Status of the offer",
        copy=False)
    partner_id = fields.Many2one('res.partner', required=True)
    property_id = fields.Many2one('estate.property', required=True)
    create_date = fields.Date(copy=False)
    validity = fields.Integer(default=7)
    date_deadline = fields.Date(string="Deadline", compute="_compute_date_deadline", inverse="_inverse_date_deadline")
    property_type_id = fields.Many2one(related="property_id.property_type_id", store=True)

    _check_expected_price = models.Constraint(
        'CHECK(price > 0)',
        'The offer price must be strictly positive.',
    )

    @api.depends('create_date', 'validity')
    def _compute_date_deadline(self):
        for record in self:
            # create_date may be false when not set yet
            if record.create_date:
                record.date_deadline = record.create_date + relativedelta(days=record.validity)
            else:
                record.date_deadline = fields.Date.context_today(record) + relativedelta(days=record.validity)
    
    @api.onchange('date_deadline')
    def _inverse_date_deadline(self):
        for record in self:
            if record.date_deadline:
                # Compute difference against create_date (or today if not yet created)
                base_date = record.create_date if record.create_date else fields.Date.context_today(record)
                record.validity = (record.date_deadline - base_date).days
            else:
                record.validity = 7
    
    def action_cancel(self):
        for record in self:
            record.status = 'refused'
        return True

    def action_confirm(self):
        for record in self:
            record.status = 'accepted'
            record.property_id.selling_price = record.price # type: ignore
            record.property_id.buyer_id = record.partner_id # type: ignore
        return True