from django.db import transaction
from rest_framework import serializers

from drf_shop_api.customers.models import (
    CustomerBonusWallet,
    CustomerCart,
    CustomerCartProduct,
    CustomerComparisonList,
    CustomerSupportRequest,
    CustomerWishList,
)
from drf_shop_api.orders.utils import total_products_price
from drf_shop_api.products.models import Product
from drf_shop_api.products.serializers import BaseProductCategorySerializer, ProductSerializer
from drf_shop_api.utils import update_related_objects


class BaseCustomerBonusWalletSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomerBonusWallet
        fields = ("id", "user", "amount")


# TODO: Add expanded serializer based on user profile serializer from parent project
class BaseCustomerWishListSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomerWishList
        fields = ("id", "user", "products", "total")

    def get_total(self, obj):
        return total_products_price(
            obj.products.all().values_list("price", flat=True),
            obj.products.all().values_list("quantity", flat=True),
        )


class CustomerWishListSerializer(BaseCustomerWishListSerializer):
    id = serializers.IntegerField(required=False)
    products = ProductSerializer(many=True)
    total = serializers.SerializerMethodField()

    @transaction.atomic
    def update(self, instance: CustomerWishList, validated_data: dict) -> CustomerWishList:
        products = validated_data.pop("products", [])
        wish_list = super().update(instance, validated_data)
        product_list = [Product.objects.get(id=product["id"]) for product in products]
        wish_list.products.set(product_list)
        return super().update(instance, validated_data)


class CustomerCartProductSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(required=False)
    product = ProductSerializer(read_only=True)

    class Meta:
        model = CustomerCartProduct
        fields = ("id", "product", "quantity")


class BaseCustomerCartSerializer(serializers.ModelSerializer):
    products = CustomerCartProductSerializer(many=True)

    class Meta:
        model = CustomerCart
        fields = ("id", "user", "products")


class CustomerCartSerializer(BaseCustomerCartSerializer):
    products = CustomerCartProductSerializer(many=True)

    @transaction.atomic
    def update(self, instance: CustomerCart, validated_data: dict) -> CustomerCart:
        products = validated_data.pop("products", None)
        cart = super().update(instance, validated_data)
        if products is not None:
            update_related_objects(self, "cart", cart, "products", products, CustomerCartProductSerializer)
        return cart


class BaseCustomerComparisonListSerializer(serializers.ModelSerializer):
    user = serializers.HiddenField(default=serializers.CurrentUserDefault())

    class Meta:
        model = CustomerComparisonList
        fields = (
            "id",
            "user",
            "category",
            "products",
        )
        read_only_fields = ("user", "category")


class CustomerComparisonListSerializer(BaseCustomerComparisonListSerializer):
    products = ProductSerializer(required=False, allow_null=True, many=True)
    category = BaseProductCategorySerializer(required=False, allow_null=True)

    @transaction.atomic
    def create(self, validated_data: dict) -> CustomerComparisonList:
        products = validated_data.pop("products", None)
        products_qs = Product.objects.filter(
            id__in=[item["id"] for item in products],
        )
        categories = set(
            products_qs.values_list("category_id", flat=True),
        )
        if len(categories) > 1:
            raise serializers.ValidationError("You cant add items from different categories to comparison in same list")
        validated_data["category_id"] = categories.pop()
        comparison = super().create(validated_data)
        for item in products_qs:
            comparison.products.add(item)
        return comparison


class BaseCustomerSupportRequestSerializer(serializers.ModelSerializer):
    user = serializers.HiddenField(default=serializers.CurrentUserDefault())

    class Meta:
        model = CustomerSupportRequest
        fields = ("id", "user", "product")


class CustomerSupportRequestSerializer(BaseCustomerSupportRequestSerializer):
    class Meta(BaseCustomerSupportRequestSerializer.Meta):
        fields = (*BaseCustomerSupportRequestSerializer.Meta.fields, "content", "created_at", "updated_at")
