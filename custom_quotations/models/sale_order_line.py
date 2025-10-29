from odoo import models, fields, api


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    total_before_discount = fields.Monetary(
        string="Total Before Coupon",
        compute="_compute_total_before_discount",
        store=True,
        currency_field='currency_id',
        readonly=True
    )

    discount_difference = fields.Monetary(
        string="Coupon Discount Value",
        compute="_compute_discount_difference",
        store=True,
        currency_field='currency_id',
        readonly=True
    )

    @api.depends('price_unit', 'product_uom_qty')
    def _compute_total_before_discount(self):
        for line in self:

            line.total_before_discount = (round((line.price_unit or 0.0) * (line.product_uom_qty or 0.0), 2))

    @api.depends('total_before_discount', 'price_subtotal')
    def _compute_discount_difference(self):
        for line in self:
            # الفرق بين السعر قبل الخصم وبعد الخصم
            line.discount_difference = round((line.total_before_discount or 0.0) - (line.price_subtotal or 0.0),2)
