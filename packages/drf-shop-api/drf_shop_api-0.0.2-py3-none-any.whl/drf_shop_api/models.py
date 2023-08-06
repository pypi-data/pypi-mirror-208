from django.db import models

from drf_shop_api.abstract_models import TimeStampedModel, TitleDescriptionModel
from drf_shop_api.customers.models import *  # noqa: F403
from drf_shop_api.orders.models import *  # noqa: F403
from drf_shop_api.products.models import *  # noqa: F403


class Currency(TitleDescriptionModel):
    dlm = models.DateTimeField(null=True, blank=True)
    is_active = models.BooleanField(default=True)
    is_main = models.BooleanField(default=False)

    class Meta:
        db_table = "currency"
        verbose_name_plural = "currencies"
        ordering = ("-id",)

    def __str__(self):
        return f"{self.title}"


class CurrencyRate(models.Model):
    from_currency = models.ForeignKey(Currency, models.CASCADE, related_name="from_rates")
    to_currency = models.ForeignKey(Currency, models.CASCADE, related_name="to_rates")
    rate = models.FloatField()
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "currency_rates"
        unique_together = ("from_currency", "to_currency")
        ordering = ("-id",)

    def __str__(self):
        return f"{self.from_currency} - {self.to_currency} {self.rate}"


class Tax(TitleDescriptionModel, TimeStampedModel):
    value = models.DecimalField(max_digits=6, decimal_places=2)

    class Meta:
        db_table = "taxes"
        verbose_name_plural = "taxes"
        ordering = ("-id",)

    def __str__(self):
        return f"{self.value}%:{self.title}"


class ShippingMethod(TitleDescriptionModel):
    logo = models.ImageField(upload_to="shipping-methods", blank=True, null=True)

    class Meta:
        db_table = "shipping-methods"
        ordering = ("-id",)

    def __str__(self):
        return f"{self.title}"
