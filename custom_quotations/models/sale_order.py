from odoo import models, fields, api
from odoo.exceptions import UserError, ValidationError
import datetime


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    template_id = fields.Many2one('quotation.template', string='Created from Template', readonly=True)
    coupon_id = fields.Many2one('coupon', string='Coupon')
    state = fields.Selection(
        selection_add=[
            ('applied_coupon', 'Coupon Applied'),
        ],
        string='Status',
        readonly=True,
        copy=False,
        tracking=True
    )
    total_before_coupon = fields.Monetary(
        string="Total Before Coupon",
        compute="_compute_total_before_coupon",
        store=True,
        readonly=True,
        currency_field='currency_id'
    )

    @api.depends('amount_untaxed', 'order_line.discount')
    def _compute_total_before_coupon(self):
        for order in self:
            total = 0.0
            for line in order.order_line:
                if not line._is_delivery():

                    total += line.price_unit * line.product_uom_qty
            order.total_before_coupon = total

    def apply_coupon(self):
        for order in self:
            if not order.coupon_id:
                raise UserError("Please select a coupon first.")

            # Save total before applying coupon
            order._compute_total_before_coupon()

            coupon = order.coupon_id
            if order.partner_id not in coupon.partner_id:
                raise UserError("You are not allowed to use this coupon.")

            if coupon.state == 'expired':
                raise UserError(f"Sorry, your coupon with code {coupon.name} is expired.")

            if coupon.used_count >= coupon.usage_limit:
                raise UserError("This coupon has reached its usage limit.")

            if coupon.days_remaining == 0:
                raise ValidationError("This coupon availability has ended!")

            if order.template_id and coupon.template_ids and order.template_id not in coupon.template_ids:
                raise UserError("This coupon is not valid for the selected quotation template.")

            if order.amount_untaxed <= 0:
                raise UserError("Cannot apply coupon to an empty or zero-value quotation.")

            if coupon.value >= order.amount_untaxed:
                raise UserError("Coupon value cannot exceed the total quotation amount.")

            discount_percentage = (coupon.value / order.amount_untaxed) * 100

            for line in order.order_line:
                if not line._is_delivery():
                    line.discount = discount_percentage

            coupon.used_count += 1
            if coupon.used_count >= coupon.usage_limit:
                coupon.state = 'expired'

            order.state = 'applied_coupon'

        return True
