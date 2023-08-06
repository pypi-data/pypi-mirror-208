from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import mixins, viewsets

from drf_shop_api.customers.filters import CustomerBonusWalletFilter, CustomerCartFilter, CustomerWishListFilter
from drf_shop_api.customers.models import (
    CustomerBonusWallet,
    CustomerCart,
    CustomerComparisonList,
    CustomerSupportRequest,
    CustomerWishList,
)
from drf_shop_api.customers.serializers import (
    BaseCustomerBonusWalletSerializer,
    BaseCustomerCartSerializer,
    BaseCustomerComparisonListSerializer,
    BaseCustomerSupportRequestSerializer,
    BaseCustomerWishListSerializer,
    CustomerCartSerializer,
    CustomerComparisonListSerializer,
    CustomerSupportRequestSerializer,
    CustomerWishListSerializer,
)
from drf_shop_api.paginators import OwnershipPaginator
from drf_shop_api.permissions import GetByAuthOrAdminEditByAdmin
from drf_shop_api.serializers import ListSerializerMixin
from drf_shop_api.utils import qs_admin_or_author


class CustomerBonusWalletViewSet(
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    mixins.UpdateModelMixin,
    viewsets.GenericViewSet,
):
    """
    list:
    All Customer wallets.

    In case of admin user list all Customer wallets
    In case of regular user return only his wallet
    Can be filtered by:`user`
    Can be ordered by: `?ordering=-amount` or `?ordering=amount`

    retrieve:
    Details of single customer wallet

    As admin retrieve customer wallet details by `id`

    update:
    Update customer wallet

    As admin update customer wallet amount
    Update customer wallet amount.

    partial_update:
    Patch customer wallet details.

    As admin update customer wallet amount
    Update customer wallet amount.
    """

    permission_classes = [GetByAuthOrAdminEditByAdmin]
    serializer_class = BaseCustomerBonusWalletSerializer
    pagination_class = OwnershipPaginator
    filter_backends = (DjangoFilterBackend,)
    filterset_class = CustomerBonusWalletFilter

    def get_queryset(self):
        return qs_admin_or_author(self, CustomerBonusWallet.objects.all())


class CustomerWishListViewSet(
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    mixins.UpdateModelMixin,
    viewsets.GenericViewSet,
):
    """
    list:
    All Customer wish lists.

    In case of admin user list all Customer wish lists
    In case of regular user return only his wish list
    Can be filtered by: `user`
    Can be ordered by: `?ordering=-amount` or `?ordering=amount`

    retrieve:
    Details of single customer wish lists

    As admin retrieve customer wish lists details by `id`

    update:
    Update customer wish lists

    As admin update customer wish lists

    partial_update:
    Patch customer wallet wish lists.

    As admin update customer wish lists
    """

    permission_classes = [GetByAuthOrAdminEditByAdmin]
    list_serializer_class = BaseCustomerWishListSerializer
    serializer_class = CustomerWishListSerializer
    pagination_class = OwnershipPaginator
    filter_backends = (DjangoFilterBackend,)
    filterset_class = CustomerWishListFilter

    def get_queryset(self):
        return qs_admin_or_author(self, CustomerWishList.objects.all())


class CustomerCartViewSet(
    ListSerializerMixin,
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    mixins.UpdateModelMixin,
    viewsets.GenericViewSet,
):
    """
    list:
    All customer carts.

    In case of admin user list all Customer cart
    In case of regular user return only his cart
    Can be filtered by: `user`

    retrieve:
    Details of single customer cart

    As admin retrieve customer cart details by `id`

    update:
    Update customer cart

    As owner you can update your cart by providing product and quantity with payload like this
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
    Update customer cart

    As owner you can update your cart
    """

    permission_classes = [GetByAuthOrAdminEditByAdmin]
    serializer_class = CustomerCartSerializer
    list_serializer_class = BaseCustomerCartSerializer
    pagination_class = OwnershipPaginator
    filter_backends = (DjangoFilterBackend,)
    filterset_class = CustomerCartFilter

    def get_queryset(self):
        return qs_admin_or_author(self, CustomerCart.objects.all())


class CustomerComparisonListViewSet(
    ListSerializerMixin,
    mixins.CreateModelMixin,
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    mixins.UpdateModelMixin,
    viewsets.GenericViewSet,
):
    """
    create:
    Create Comparison list

    As authenticated user you can create comparison list

    ```
    ```

    list:
    All comparison lists.

    In case of admin user list all comparison lists
    In case of regular user return only his comparison lists

    retrieve:
    Details of single comparison list

    As admin retrieve comparison list details by `id`



    partial_update:
    Update comparison list

    As owner you can update your comparison list
    """

    permission_classes = (GetByAuthOrAdminEditByAdmin,)
    serializer_class = CustomerComparisonListSerializer
    list_serializer_class = BaseCustomerComparisonListSerializer
    pagination_class = OwnershipPaginator
    filter_backends = (DjangoFilterBackend,)

    def get_queryset(self):
        return qs_admin_or_author(self, CustomerComparisonList.objects.all())


class CustomerSupportRequestViewSet(
    ListSerializerMixin,
    mixins.CreateModelMixin,
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    mixins.UpdateModelMixin,
    viewsets.GenericViewSet,
):
    permission_classes = (GetByAuthOrAdminEditByAdmin,)
    serializer_class = CustomerSupportRequestSerializer
    list_serializer_class = BaseCustomerSupportRequestSerializer
    pagination_class = OwnershipPaginator
    filter_backends = (DjangoFilterBackend,)

    def get_queryset(self):
        return qs_admin_or_author(self, CustomerSupportRequest.objects.all())
