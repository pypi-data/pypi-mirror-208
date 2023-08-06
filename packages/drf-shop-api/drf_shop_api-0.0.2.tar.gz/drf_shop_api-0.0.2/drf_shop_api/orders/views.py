from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import mixins, viewsets

from drf_shop_api.orders.models import Order
from drf_shop_api.orders.serializers import BaseOrderSerializer, OrderSerializer
from drf_shop_api.paginators import OwnershipPaginator
from drf_shop_api.permissions import GetByAuthOrAdminEditByAdmin
from drf_shop_api.serializers import ListSerializerMixin
from drf_shop_api.utils import qs_admin_or_author


class OrderViewSet(
    ListSerializerMixin,
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    mixins.CreateModelMixin,
    mixins.UpdateModelMixin,
    viewsets.GenericViewSet,
):
    """
    create:
    Create order

    As authenticated user you can create order by providing product and quantity

    list:
    All orders.

    In case of admin user list all orders
    In case of regular user return only his orders

    retrieve:
    Details of single customer order

    As admin retrieve customer order details by `id`

    update:
    Update order

    As owner you can update your order by providing product and quantity with payload like this
    ```
    {"id": 10,
    "user": 63,
    "products": [
        {"id": 10, "product":
                {"id": 10,
                "price": "100.00",
                "title": "Where Find Dinner Indeed Street Until",
                "description": null, "comments": [],
                "main_image": {"image": null, "is_main": false},
                "currency": {"title": "Seven Operation Thank Development Defense Term"},
                "category": {"title": "Last Simple Include Do Wonder Not","url": "last-simple-include-do-wonder-not"},
                "images": [],
                "properties": []},
                "quantity": 15}
        ]}
    ```

    partial_update:
    Update order

    As owner you can update your order
    """

    permission_classes = [GetByAuthOrAdminEditByAdmin]
    serializer_class = OrderSerializer
    list_serializer_class = BaseOrderSerializer
    pagination_class = OwnershipPaginator
    filter_backends = (DjangoFilterBackend,)
    # filterset_class = OrderFilter

    def get_queryset(self):
        return qs_admin_or_author(self, Order.objects.all())
