from django_filters import rest_framework as filters

from drf_shop_api.customers.models import CustomerBonusWallet, CustomerCart, CustomerWishList


class CustomerBonusWalletFilter(filters.FilterSet):
    user = filters.NumberFilter(field_name="user")
    ordering = filters.OrderingFilter(
        fields=(("amount", "amount"),),
        field_labels={
            "amount": "Amount of money on wallet",
        },
    )

    class Meta:
        model = CustomerBonusWallet
        fields = ("user", "amount")


# TODO : Add sorting by aggregated price of all items
class CustomerWishListFilter(filters.FilterSet):
    user = filters.NumberFilter(field_name="user")
    products = filters.NumberFilter(field_name="products")

    class Meta:
        model = CustomerWishList
        fields = ("user", "products")


class CustomerCartFilter(filters.FilterSet):
    user = filters.NumberFilter(field_name="user")
    products = filters.NumberFilter(field_name="products__product")

    class Meta:
        model = CustomerCart
        fields = ("user", "products")
