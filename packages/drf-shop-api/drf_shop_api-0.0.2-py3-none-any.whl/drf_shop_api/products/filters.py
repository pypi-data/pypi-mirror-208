from django_filters import rest_framework as filters

from drf_shop_api.products.models import Product, ProductComment, Property


class ProductFilter(filters.FilterSet):
    title = filters.CharFilter(field_name="title", lookup_expr="icontains")
    price_min = filters.NumberFilter(field_name="price", lookup_expr="gte", distinct=True)
    price_max = filters.NumberFilter(field_name="price", lookup_expr="lte", distinct=True)
    category = filters.CharFilter(field_name="category__url", lookup_expr="exact")

    class Meta:
        model = Product
        fields = ("title", "price", "category")


class PropertyFilter(filters.FilterSet):
    title = filters.CharFilter(field_name="title", lookup_expr="icontains")
    unit = filters.CharFilter(field_name="unit", lookup_expr="icontains")

    class Meta:
        model = Property
        fields = ("title", "unit")


class ProductCommentFilter(filters.FilterSet):
    product = filters.NumberFilter(field_name="product", lookup_expr="exact")
    user = filters.NumberFilter(field_name="user", lookup_expr="exact")

    class Meta:
        model = ProductComment
        fields = ("product", "user")
