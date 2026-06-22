from odoo import fields, models
from odoo.fields import Command

class EstateProperty(models.Model):
    _inherit = ['estate.property']

    def action_sold(self):
        for record in self:
            invoice_lines = []
            invoice_lines.append(Command.create({
                'name': 'Percentage Fee',
                'quantity': 1.0,
                'price_unit': record.selling_price * 0.06 # type: ignore
            }))
            invoice_lines.append(Command.create({
                'name': 'Administrative Fee',
                'quantity': 1.0,
                'price_unit': 100.0
            }))

            self.env['account.move'].create({
                'move_type': 'out_invoice',
                'partner_id': record.buyer_id.id, # type: ignore
                'invoice_date': fields.Date.today(),
                'invoice_line_ids': invoice_lines,
            })

        return super().action_sold() # type: ignore