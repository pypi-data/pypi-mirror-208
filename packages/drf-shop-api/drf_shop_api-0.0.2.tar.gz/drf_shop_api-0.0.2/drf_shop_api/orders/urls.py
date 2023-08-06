from rest_framework.routers import SimpleRouter

from drf_shop_api.orders.views import OrderViewSet

app_name = "orders"

router = SimpleRouter()
router.register("", OrderViewSet, basename="orders")

urlpatterns = [
    *router.urls,
]
