from drf_shop_api.customers.models import CustomerBonusWallet, CustomerCart, CustomerWishList


def create_shop_profile(func):
    """Create shop profile

    Creates all necessary models for drf-shop-api

    Args:
        func (_type_): _description_
    """

    def wrapper(self, *args, **kwargs):
        user = func(self, *args, **kwargs)
        CustomerWishList.objects.create(user=user)
        CustomerBonusWallet.objects.create(user=user)
        CustomerCart.objects.create(user=user)
        return user

    return wrapper
