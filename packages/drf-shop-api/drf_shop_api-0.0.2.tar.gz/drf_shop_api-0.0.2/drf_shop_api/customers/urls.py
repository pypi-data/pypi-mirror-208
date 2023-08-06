from rest_framework.routers import SimpleRouter

from drf_shop_api.customers.views import (
    CustomerBonusWalletViewSet,
    CustomerCartViewSet,
    CustomerComparisonListViewSet,
    CustomerSupportRequestViewSet,
    CustomerWishListViewSet,
)

app_name = "customers"

router = SimpleRouter()
router.register("bonus-wallets", CustomerBonusWalletViewSet, basename="bonus-wallets")
router.register("wishlists", CustomerWishListViewSet, basename="wishlists")
router.register("carts", CustomerCartViewSet, basename="carts")
router.register("comparisons", CustomerComparisonListViewSet, basename="comparisons")
router.register("support-request", CustomerSupportRequestViewSet, basename="support-request")
urlpatterns = [
    *router.urls,
]
