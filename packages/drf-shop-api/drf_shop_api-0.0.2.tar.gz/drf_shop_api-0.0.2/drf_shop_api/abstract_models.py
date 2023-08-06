from django.conf import settings
from django.db import models
from django.utils.translation import gettext_lazy as _


class DescriptionModel(models.Model):
    description = models.TextField(_("description"), null=True, blank=True)

    class Meta:
        abstract = True


class TitleModel(models.Model):
    """Title

    Model with extra ``title`` field that is required

    """

    title = models.CharField(max_length=50)

    class Meta:
        abstract = True


class TitleDescriptionModel(TitleModel, DescriptionModel):
    """TitleDescriptionModel

    This models contains:

    ``title`` and optional ``description`` field to use in your models

    """

    class Meta:
        abstract = True


class TimeStampedModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class OwnershipSingleModel(models.Model):
    """Add relation to project auth user for single instance

    For example:

    CustomerBonusWallet can be accessed via:

    ``user.customerbonuswallet``
    """

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        blank=True,
        null=True,
        on_delete=models.CASCADE,
        related_name="%(class)s",
    )

    class Meta:
        abstract = True


class OwnershipMultipleModel(models.Model):
    """Add relation to project auth user for multiple instance

    For example:

    CustomerBonusWallet can be accessed via:

    ``user.customerwishlist``
    """

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="%(class)s")

    class Meta:
        abstract = True


class AbstractPayment(OwnershipMultipleModel):
    total_price = models.FloatField(null=True, blank=True)
    is_refundable = models.BooleanField(default=True)
    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True
