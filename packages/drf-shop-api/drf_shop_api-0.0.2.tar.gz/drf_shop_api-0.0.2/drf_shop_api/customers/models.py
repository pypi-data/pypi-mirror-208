from django.core.validators import MinValueValidator
from django.db import models

from drf_shop_api.abstract_models import (
    OwnershipMultipleModel,
    OwnershipSingleModel,
    TimeStampedModel,
    TitleDescriptionModel,
)
from drf_shop_api.products.models import Product, ProductCategory


class CustomerBonusWallet(OwnershipSingleModel):
    amount = models.DecimalField(max_digits=6, decimal_places=2, default=0, validators=[MinValueValidator(0)])

    class Meta:
        db_table = "customer-bonus-wallets"
        ordering = ("-id",)


class CustomerWishList(OwnershipMultipleModel, TimeStampedModel, TitleDescriptionModel):
    products = models.ManyToManyField(Product, blank=True)

    class Meta:
        db_table = "customer-wish-lists"
        ordering = ("-id",)


class CustomerCart(OwnershipSingleModel, TimeStampedModel):
    class Meta:
        db_table = "customer-carts"
        ordering = ("-id",)


class CustomerCartProduct(models.Model):
    cart = models.ForeignKey(CustomerCart, models.CASCADE, related_name="products")
    product = models.ForeignKey(Product, models.CASCADE)
    quantity = models.IntegerField(default=1)

    class Meta:
        db_table = "customer-cart-products"
        unique_together = ["cart", "product"]
        ordering = ("-id",)


class CustomerSupportRequest(OwnershipMultipleModel, TimeStampedModel):
    content = models.TextField()
    product = models.ForeignKey(Product, models.CASCADE, blank=True, null=True, related_name="related_product")

    class Meta:
        db_table = "customer-support-requests"
        ordering = ("-id",)


class CustomerComparisonList(OwnershipMultipleModel):
    category = models.OneToOneField(ProductCategory, models.CASCADE, related_name="comparisons", unique=True)
    products = models.ManyToManyField(Product, blank=True)

    class Meta:
        db_table = "customer-comparison-lists"
        ordering = ("-id",)
