from rest_framework import serializers

from drf_shop_api.products.models import (
    Product,
    ProductCategory,
    ProductComment,
    ProductImage,
    ProductProperty,
    Property,
)
from drf_shop_api.serializers import BaseCurrencySerializer


class BaseProductCommentSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductComment
        fields = ("id",)


class ProductCommentSerializer(BaseProductCommentSerializer):
    user = serializers.HiddenField(default=serializers.CurrentUserDefault())
    product = serializers.PrimaryKeyRelatedField(queryset=Product.objects.all())

    class Meta(BaseProductCommentSerializer.Meta):
        fields = (*BaseProductCommentSerializer.Meta.fields, "product", "content", "user")


class ProductImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductImage
        fields = (
            "id",
            "image",
            "is_main",
        )


class BasePropertySerializer(serializers.ModelSerializer):
    class Meta:
        model = Property
        fields = (
            "id",
            "title",
        )


class PropertySerializer(BasePropertySerializer):
    class Meta(BasePropertySerializer.Meta):
        fields = (*BasePropertySerializer.Meta.fields, "unit", "description")


class ProductPropertySerializer(serializers.ModelSerializer):
    property = PropertySerializer(many=False)

    class Meta:
        model = ProductProperty
        fields = ("property", "value")


class BaseProductCategorySerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(required=False)

    class Meta:
        model = ProductCategory
        fields = ("id", "title", "url")


class BaseProductSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(required=False)
    main_image = serializers.SerializerMethodField()
    category = BaseProductCategorySerializer(many=False, read_only=True)
    comments = BaseProductCommentSerializer(many=True)
    currency = BaseCurrencySerializer(many=False)

    class Meta:
        model = Product
        fields = ("id", "price", "title", "description", "comments", "main_image", "currency", "category")

    def get_main_image(self, obj):
        return ProductImageSerializer(obj.images.filter(is_main=True).first()).data


class ProductSerializer(BaseProductSerializer):
    images = ProductImageSerializer(many=True)
    properties = ProductPropertySerializer(many=True)
    comments = ProductCommentSerializer(many=True)

    class Meta(BaseProductSerializer.Meta):
        fields = (*BaseProductSerializer.Meta.fields, "images", "properties")
