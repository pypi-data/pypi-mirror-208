from rest_framework.routers import SimpleRouter

from drf_shop_api.products.views import ProductCommentViewSet, ProductViewSet, PropertyViewSet

app_name = "products"

router = SimpleRouter()
router.register("products", ProductViewSet, basename="products")
router.register("properties", PropertyViewSet, basename="properties")
router.register("comments", ProductCommentViewSet, basename="comments")
urlpatterns = [
    *router.urls,
]
