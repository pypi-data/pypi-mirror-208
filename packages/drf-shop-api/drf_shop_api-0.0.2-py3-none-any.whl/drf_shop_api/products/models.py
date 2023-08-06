from django.core.validators import MinValueValidator
from django.db import models
from django.utils.text import slugify

from drf_shop_api.abstract_models import OwnershipMultipleModel, TimeStampedModel, TitleDescriptionModel
from drf_shop_api.products.constants import Units


class ProductCategory(TitleDescriptionModel, TimeStampedModel):
    url = models.SlugField(unique=True, max_length=255)
    parent = models.ForeignKey("self", on_delete=models.CASCADE, null=True, blank=True, related_name="children")
    is_active = models.BooleanField(default=True)

    class Meta:
        db_table = "product-categories"
        indexes = [models.Index(fields=["url"])]
        verbose_name_plural = "Product categories"

    def is_parent_category(self):
        return bool(self.parent is None)

    @property
    def parent_category_id(self):
        return self.parent.id if self.parent is not None else None

    def save(self, *args, **kwargs):
        self.url = slugify(self.title)
        super(ProductCategory, self).save(*args, **kwargs)


class Product(TitleDescriptionModel, TimeStampedModel):
    price = models.DecimalField(max_digits=6, decimal_places=2, validators=[MinValueValidator(0)])
    currency = models.ForeignKey("drf_shop_api.Currency", on_delete=models.CASCADE)
    category = models.ForeignKey(ProductCategory, on_delete=models.CASCADE)
    is_active = models.BooleanField(default=True)
    quantity = models.IntegerField(default=1)

    class Meta:
        db_table = "products"
        ordering = ("-id",)

    def __str__(self) -> str:
        return f"{self.title}: {self.price}"


class ProductImage(models.Model):
    product = models.ForeignKey(Product, models.CASCADE, related_name="images")
    image = models.ImageField()
    is_main = models.BooleanField(default=False)

    class Meta:
        db_table = "product-images"


class Property(TitleDescriptionModel):
    unit = models.CharField(max_length=255, choices=[(v.name, v.value) for v in Units], null=True, blank=True)

    class Meta:
        db_table = "properties"
        ordering = ("-id",)
        verbose_name_plural = "Properties"

    def __str__(self):
        return f"{self.title} ({self.unit})" if self.unit else self.title


class ProductProperty(models.Model):
    product = models.ForeignKey(Product, models.CASCADE, related_name="properties")
    property = models.ForeignKey(Property, models.CASCADE)
    value = models.CharField(max_length=200)

    class Meta:
        db_table = "product-properties"
        ordering = ("-id",)
        verbose_name_plural = "Product properties"


class ProductComment(OwnershipMultipleModel):
    product = models.ForeignKey(Product, models.CASCADE, related_name="comments")
    content = models.TextField()

    class Meta:
        db_table = "product-comments"
        ordering = ("-id",)
