from django.db import transaction
from rest_framework import serializers

from drf_shop_api.models import ShippingMethod
from drf_shop_api.orders.models import Order, OrderProduct, OrderShipping
from drf_shop_api.orders.utils import total_products_price
from drf_shop_api.products.models import Product
from drf_shop_api.products.serializers import ProductSerializer
from drf_shop_api.serializers import BaseShippingMethodSerializer
from drf_shop_api.utils import nested_write, update_related_objects


class BaseOrderShippingSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(required=False)
    method = BaseShippingMethodSerializer(required=False, allow_null=True)

    class Meta:
        model = OrderShipping
        fields = ("id", "method", "address", "status")
        read_only_fields = ("method",)

    def create(self, validated_data: dict):
        validated_data = nested_write(validated_data, "method", ShippingMethod)
        return super().create(validated_data)

    def update(self, instance, validated_data: dict):
        validated_data = nested_write(validated_data, "method", ShippingMethod)
        return super().update(instance, validated_data)


class OrderProductSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(required=False)
    product = ProductSerializer(required=False, allow_null=True)

    class Meta:
        model = OrderProduct
        fields = ("id", "product", "quantity")
        read_only_fields = ("product",)

    def create(self, validated_data: dict):
        validated_data = nested_write(validated_data, "product", Product)
        return super().create(validated_data)

    def update(self, instance, validated_data):
        validated_data = nested_write(validated_data, "product", Product)
        return super().update(instance, validated_data)


class BaseOrderSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = ("id", "user", "products", "shipping", "total")
        read_only_fields = ("user",)


class OrderSerializer(BaseOrderSerializer):
    user = serializers.HiddenField(default=serializers.CurrentUserDefault())
    products = OrderProductSerializer(many=True)
    shipping = BaseOrderShippingSerializer(required=True)

    @transaction.atomic
    def create(self, validated_data: dict) -> Order:
        order_products = validated_data.pop("products", [])
        order_products_serializer = OrderProductSerializer(data=order_products, many=True, context=self.context)
        order_shipping = validated_data.pop("shipping", None)
        order_shipping_serializer = BaseOrderShippingSerializer(data=order_shipping, context=self.context)
        order = super().create(validated_data)
        if order_products_serializer.is_valid():
            order_products_serializer.save(order=order)
        if order_shipping_serializer.is_valid():
            order_shipping_serializer.save(order=order)
        quantities = [product["quantity"] for product in order_products]
        prices = [item["product"]["price"] for _ in order_products for item in order_products]
        order.total = total_products_price(prices, quantities)
        return order

    @transaction.atomic
    def update(self, instance: Order, validated_data: dict) -> Order:
        order_products = validated_data.pop("products", None)
        order_shipping = validated_data.pop("shipping", None)
        order = super().update(instance, validated_data)
        if order_products is not None:
            update_related_objects(self, "order", order, "products", order_products, OrderProductSerializer)
        if order_shipping is not None:
            old_shipping = OrderShipping.objects.get(order=instance)
            new_shipping = BaseOrderShippingSerializer(data=order_shipping, context=self.context)
            if new_shipping.is_valid():
                old_shipping.delete()
                new_shipping.save(order=order)
        quantities = [product["quantity"] for product in order_products]
        prices = [item["product"]["price"] for _ in order_products for item in order_products]
        order.total = total_products_price(prices, quantities)
        return order
