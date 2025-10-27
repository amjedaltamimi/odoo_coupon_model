# custom_quotations/models/quotation_template.py
from email.policy import default

from odoo import models, fields, api

class QuotationTemplate(models.Model):
    _name = 'quotation.template'
    _description = 'Quotation Template'

    name = fields.Char(string='Template Name' ,readonly=True,default="New")
    template_line_ids = fields.One2many('quotation.template.line', 'template_id', string='Template Lines')
    sales_order_count = fields.Integer(
        string="Sales Orders",
        compute="_compute_sales_order_count")

    def _compute_sales_order_count(self):
        for template in self:
            template.sales_order_count = self.env['sale.order'].search_count([('template_id', '=', template.id)])

    # def action_view_sales_orders(self):
    #     self.ensure_one()
    #     return {
    #         'name': 'Sales Orders',
    #         'type': 'ir.actions.act_window',
    #         'res_model': 'sale.order',
    #         'view_mode': 'list,form',
    #         'domain': [('template_id', '=', self.id)],
    #     }
    def action_open_quotations(self):
        self.ensure_one()
        return {
                'name': 'Sales Orders',
                'type': 'ir.actions.act_window',
                'res_model': 'sale.order',
                'view_mode': 'list,form',
                'domain': [('template_id', '=', self.id)],
            }
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
    @api.model
    def create(self,vals):
        res=super(QuotationTemplate,self).create(vals)
        if res.name=="New":
          res.name= self.env['ir.sequence'].next_by_code("temp.seq")
        return res

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
