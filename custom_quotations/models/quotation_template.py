# custom_quotations/models/quotation_template.py
from odoo import models, fields, api

class QuotationTemplate(models.Model):
    _name = 'quotation.template'
    _description = 'Quotation Template'

    name = fields.Char(string='Template Name', required=True)
    template_line_ids = fields.One2many('quotation.template.line', 'template_id', string='Template Lines')


    def generate_quotation(self):
        self.ensure_one()

        order_lines = []
        for line in self.template_line_ids:
            order_lines.append((0, 0, {
                'product_id': line.product_id.id,
                'name': line.name,
                'product_uom_qty': line.quantity,
                'price_unit': line.price_unit,
            }))

        quotation = self.env['sale.order'].create({
            'partner_id': self.env.user.partner_id.id,
            'order_line': order_lines,
            'template_id': self.id,
        })


        return {
            'type': 'ir.actions.act_window',
            'name': 'Quotation',
            'res_model': 'sale.order',
            'res_id': quotation.id,
            'view_mode': 'form',
            'target': 'current',
        }

class QuotationTemplateLine(models.Model):
    _name = 'quotation.template.line'
    _description = 'Quotation Template Line'


    template_id = fields.Many2one('quotation.template', string='Template', required=True, ondelete='cascade')
    product_id = fields.Many2one('product.product', string='Product', required=True)
    name = fields.Text(string='Description', required=True)
    quantity = fields.Float(string='Quantity', default=1.0)
    price_unit = fields.Float(string='Unit Price')


    @api.onchange('product_id')
    def _onchange_product_id(self):
        if self.product_id:
            self.name = self.product_id.name
            self.price_unit = self.product_id.list_price
