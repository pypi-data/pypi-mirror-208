from django.conf import settings
from django.core.validators import MinValueValidator
from django.db import models

from drf_shop_api.abstract_models import OwnershipMultipleModel, TimeStampedModel
from drf_shop_api.orders.constants import OrderStatus, PaymentStatus, ShipmentStatus
from drf_shop_api.products.models import Product


class Order(TimeStampedModel, OwnershipMultipleModel):
    status = models.CharField(
        max_length=255,
        choices=[(v.name, v.value) for v in OrderStatus],
        null=True,
        blank=True,
        default=OrderStatus.CREATED.name,
    )
    total = models.DecimalField(max_digits=6, default=0, decimal_places=2, validators=[MinValueValidator(0)])

    class Meta:
        db_table = "orders"
        ordering = ("-id",)


class OrderShipping(models.Model):
    order = models.OneToOneField(Order, models.CASCADE, related_name="shipping")
    method = models.ForeignKey("drf_shop_api.ShippingMethod", models.CASCADE)
    address = models.CharField(max_length=255)
    status = models.CharField(
        max_length=255,
        choices=[(v.name, v.value) for v in ShipmentStatus],
        null=True,
        blank=True,
        default=ShipmentStatus.CREATED.name,
    )

    class Meta:
        db_table = "order-shippings"
        ordering = ("-id",)


class OrderPayment(models.Model):
    order = models.OneToOneField(Order, models.CASCADE, related_name="payment")
    if settings.DRF_SHOP_PAYMENT_MODEL:
        payment = models.ForeignKey(settings.DRF_SHOP_PAYMENT_MODEL, models.CASCADE)
    else:
        status = models.CharField(
            max_length=255,
            choices=[(v.name, v.value) for v in PaymentStatus],
            null=True,
            blank=True,
            default=PaymentStatus.UNCOMPLETED.name,
        )


class OrderProduct(models.Model):
    order = models.ForeignKey(Order, models.CASCADE, related_name="products")
    product = models.ForeignKey(Product, models.CASCADE, related_name="order_products")
    quantity = models.IntegerField(default=1)

    class Meta:
        db_table = "order-products"
        ordering = ("-id",)
