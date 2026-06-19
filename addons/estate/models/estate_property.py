from odoo import fields, models, api
from dateutil.relativedelta import relativedelta

class EstateProperty(models.Model):
    _name = "estate.property"
    _description = "Estate Property"

    active = fields.Boolean(default=True)
    name = fields.Char(required=True)
    description = fields.Text()
    postcode = fields.Char()
    date_availability = fields.Date(copy=False, default=fields.Date.today() + relativedelta(months=3))
    expected_price = fields.Float(required=True)
    selling_price = fields.Float(readonly=True, copy=False)
    bedrooms = fields.Integer(default=2)
    living_area = fields.Integer(string="Living Area (sqm)")
    facades = fields.Integer()
    garage = fields.Boolean()
    garden = fields.Boolean()
    garden_area = fields.Integer(string="Garden Area (sqm)")
    garden_orientation = fields.Selection(
        string='Garden Orientation',
        selection=[
            ('north', 'North'), 
            ('south', 'South'), 
            ('east', 'East'), 
            ('west', 'West')], # type: ignore
        help="The orientation of the garden")
    state = fields.Selection(
        string='State',
        selection=[
            ('new', 'New'), 
            ('offer_received', 'Offer Received'), 
            ('offer_accepted', 'Offer Accepted'), 
            ('sold', 'Sold'),
            ('cancelled', 'Cancelled')], # type: ignore
        help="The state of the property",
        required=True,
        copy=False,
        default='new')
    property_type_id = fields.Many2one("estate.property.type", string="Property Type")
    buyer_id = fields.Many2one('res.users', string='Buyer', copy=False)
    salesperson_id = fields.Many2one('res.users', string='Salesperson', default=lambda self: self.env.user)
    tag_ids = fields.Many2many("estate.property.tag", string="Tags")
    offer_ids = fields.One2many("estate.property.offer", "property_id", string="Offers")
    total_area = fields.Integer(string="Total Area (sqm)", readonly=True, compute="_compute_total_area")
    best_price = fields.Float(readonly=True, compute="_compute_best_price")

    @api.depends('living_area', 'garden_area')
    def _compute_total_area(self):
        for line in self:
            line.total_area = line.living_area + line.garden_area
    
    @api.depends('offer_ids')
    def _compute_best_price(self):
        for line in self:
            line.best_price = max(line.offer_ids.mapped('price'))
    
    @api.onchange('garden')
    def _onchange_garden(self):
        if self.garden:
            self.garden_area = 10
            self.garden_orientation = "north"
        else:
            self.garden_area = 0
            self.garden_orientation = False