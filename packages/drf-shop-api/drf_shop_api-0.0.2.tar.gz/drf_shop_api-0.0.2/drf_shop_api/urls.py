from django.urls import include, path

api_urlpatterns = [
    path("products/", include("drf_shop_api.products.urls")),
    path("customers/", include("drf_shop_api.customers.urls")),
    path("orders/", include("drf_shop_api.orders.urls")),
]


urlpatterns = [
    path("", include(api_urlpatterns)),
]
