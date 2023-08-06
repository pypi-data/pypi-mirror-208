from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import mixins, viewsets

from drf_shop_api.paginators import ResultSetPagination
from drf_shop_api.permissions import GetByAnyCreateByAuthEditByOwner, IsAdminOrReadOnly
from drf_shop_api.products.filters import ProductFilter, PropertyFilter
from drf_shop_api.products.models import Product, ProductComment, Property
from drf_shop_api.products.serializers import (
    BaseProductCommentSerializer,
    BaseProductSerializer,
    BasePropertySerializer,
    ProductCommentSerializer,
    ProductSerializer,
    PropertySerializer,
)
from drf_shop_api.serializers import ListSerializerMixin


class ProductViewSet(
    ListSerializerMixin,
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    mixins.UpdateModelMixin,
    mixins.DestroyModelMixin,
    viewsets.GenericViewSet,
):
    """
    list:
    All products.

    List all properties, with filtering by:
    `title`, `price`

    retrieve:
    Details of single product

    Retrieve details of product

    update:
    Update product details.

    Update product

    partial_update:
    Patch product details.

    Patch details of product.

    destroy:
    Delete product.

    Patch details of product.
    """

    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    permission_classes = [IsAdminOrReadOnly]
    list_serializer_class = BaseProductSerializer
    pagination_class = ResultSetPagination
    filter_backends = (DjangoFilterBackend,)
    filterset_class = ProductFilter


class ProductCommentViewSet(
    ListSerializerMixin,
    mixins.CreateModelMixin,
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    mixins.UpdateModelMixin,
    mixins.DestroyModelMixin,
    viewsets.GenericViewSet,
):
    """
    list:
    All product comments.

    List all product comment, with filtering by:
    `product`, `user`

    retrieve:
    Details of product comment

    Retrieve details of product comment


    create:
    Create product comment

    Creates a product comment for specific product

    update:
    Update product details.

    Update product

    partial_update:
    Patch product details.

    Patch details of product.

    destroy:
    Delete product.

    Patch details of product.
    """

    queryset = ProductComment.objects.all()
    serializer_class = ProductCommentSerializer
    permission_classes = [GetByAnyCreateByAuthEditByOwner]
    list_serializer_class = BaseProductCommentSerializer
    pagination_class = ResultSetPagination
    filter_backends = (DjangoFilterBackend,)
    filter_class = ProductFilter


class PropertyViewSet(
    ListSerializerMixin,
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    mixins.UpdateModelMixin,
    mixins.DestroyModelMixin,
    viewsets.GenericViewSet,
):
    """
    list:
    All properties.

    List all properties, with filtering by:
    `title`, `unit`

    retrieve:
    Details of single property

    Retrieve details of property

    update:
    Update property details.

    Update property

    partial_update:
    Patch property details.

    Patch details of property.

    destroy:
    Delete property.

    Patch details of property.
    """

    queryset = Property.objects.all()
    serializer_class = PropertySerializer
    list_serializer_class = BasePropertySerializer
    pagination_class = ResultSetPagination
    filter_backends = (DjangoFilterBackend,)
    filterset_class = PropertyFilter
