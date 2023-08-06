from django.contrib import admin

from drf_shop_api.customers.models import CustomerSupportRequest
from drf_shop_api.orders.models import OrderPayment

from .models import (
    Currency,
    CurrencyRate,
    CustomerBonusWallet,
    CustomerCart,
    CustomerCartProduct,
    CustomerWishList,
    Order,
    OrderProduct,
    OrderShipping,
    Product,
    ProductCategory,
    ProductComment,
    ProductImage,
    ProductProperty,
    Property,
    ShippingMethod,
    Tax,
)


@admin.register(CustomerSupportRequest)
class CustomerSupportRequestAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "created_at",
        "updated_at",
    )
    list_filter = (
        "created_at",
        "updated_at",
    )


@admin.register(ProductCategory)
class ProductCategoryAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "description",
        "title",
        "created_at",
        "updated_at",
        "url",
        "parent",
        "is_active",
    )
    list_filter = ("created_at", "updated_at", "parent", "is_active")
    date_hierarchy = "created_at"


class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 3


class ProductPropertyInline(admin.TabularInline):
    model = ProductProperty
    extra = 1


class ProductCommentInline(admin.TabularInline):
    model = ProductComment
    extra = 1


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "description",
        "title",
        "created_at",
        "updated_at",
        "price",
        "currency",
        "category",
        "is_active",
    )
    list_filter = (
        "created_at",
        "updated_at",
        "currency",
        "category",
        "is_active",
    )
    inlines = (
        ProductImageInline,
        ProductPropertyInline,
        ProductCommentInline,
    )
    date_hierarchy = "created_at"


@admin.register(Property)
class PropertyAdmin(admin.ModelAdmin):
    list_display = ("id", "description", "title", "unit")


@admin.register(CustomerBonusWallet)
class CustomerBonusWalletAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "amount")
    list_filter = ("user",)


@admin.register(CustomerWishList)
class CustomerWishListAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "description",
        "title",
        "created_at",
        "updated_at",
        "user",
    )
    list_filter = ("created_at", "updated_at", "user")
    raw_id_fields = ("products",)
    date_hierarchy = "created_at"


class CustomerCartProductInline(admin.TabularInline):
    model = CustomerCartProduct


@admin.register(CustomerCart)
class CustomerCartAdmin(admin.ModelAdmin):
    list_display = ("id", "created_at", "updated_at", "user")
    inlines = [
        CustomerCartProductInline,
    ]
    list_filter = ("created_at", "updated_at", "user")
    date_hierarchy = "created_at"


class OrderShippingInline(admin.TabularInline):
    model = OrderShipping


class OrderProductInline(admin.TabularInline):
    model = OrderProduct


class OrderPaymentInline(admin.TabularInline):
    model = OrderPayment


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ("id", "created_at", "updated_at", "user", "status")
    list_filter = ("created_at", "updated_at", "user")
    inlines = [
        OrderShippingInline,
        OrderProductInline,
        OrderPaymentInline,
    ]
    date_hierarchy = "created_at"


@admin.register(Currency)
class CurrencyAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "description",
        "title",
        "dlm",
        "is_active",
        "is_main",
    )
    list_filter = ("dlm", "is_active", "is_main")


@admin.register(CurrencyRate)
class CurrencyRateAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "from_currency",
        "to_currency",
        "rate",
        "is_active",
        "created_at",
    )
    list_filter = ("from_currency", "to_currency", "is_active", "created_at")
    date_hierarchy = "created_at"


@admin.register(Tax)
class TaxAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "description",
        "title",
        "created_at",
        "updated_at",
        "value",
    )
    list_filter = ("created_at", "updated_at")
    date_hierarchy = "created_at"


@admin.register(ShippingMethod)
class ShippingMethodAdmin(admin.ModelAdmin):
    list_display = ("id", "description", "title", "logo")
