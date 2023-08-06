from django.apps import apps
from django.conf import settings
from django.urls import reverse
from mixer.backend.django import mixer

from drf_shop_api.models import ShippingMethod
from drf_shop_api.orders.models import Order, OrderProduct, OrderShipping
from drf_shop_api.products.models import Product
from drf_shop_api.products.serializers import ProductSerializer
from drf_shop_api.serializers import BaseShippingMethodSerializer
from drf_shop_api.tests import BaseAPITest


class TestOrderCase(BaseAPITest):
    def setUp(self):
        self.admin = self.create_and_login(email="admin@example.com", is_staff=True, is_superuser=True)
        self.order_count: int = 10
        self.list_url: str = reverse("orders:orders-list")
        self.shipping_method = mixer.blend(ShippingMethod)
        user_list = mixer.cycle(self.order_count).blend(
            apps.get_model(f"{settings.AUTH_USER_MODEL}"),
            is_active=True,
        )
        product_list = []
        for i in range(self.order_count):
            product_list.append(mixer.blend(Product, price=(i + 1) * 10))
        for i, user in zip(range(self.order_count), user_list):
            _ = mixer.blend(Order, user=user)
            mixer.blend(OrderProduct, order=_, product=product_list[i])
            mixer.blend(OrderShipping, order=_, method=self.shipping_method)
        self.target = Order.objects.first()

    def test_list_admin(self):
        resp = self.client.get(self.list_url)
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.data["count"], self.order_count)

    def test_list_admin_custom_page_size(self):
        qty = 5
        resp = self.client.get(f"{self.list_url}?page_size={qty}")
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(len(resp.data["results"]), qty)

    def test_list_admin_custom_page_size_and_page(self):
        qty = 6
        page_count = self.order_count - qty
        resp = self.client.get(f"{self.list_url}?page=2&page_size={qty}")
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(len(resp.data["results"]), page_count)

    def test_detail_admin(self):
        resp = self.client.get(f"{self.list_url}{self.target.id}/")
        self.assertEqual(resp.status_code, 200)

    def test_create_order(self):
        product = Product.objects.first()
        data = {
            "shipping": {"address": "Home", "method": BaseShippingMethodSerializer(self.shipping_method).data},
            "products": [{"product": ProductSerializer(product).data, "quantity": 10}],
            "total": 1,
        }
        self.authorize(self.target.user)
        resp = self.client.post(f"{self.list_url}", data)
        self.assertEqual(resp.status_code, 201)
        self.assertEqual(float(resp.data["total"]), product.price * 10)

    def test_update_order_products(self):
        product = Product.objects.first()
        data = {
            "shipping": {"address": "Home", "method": BaseShippingMethodSerializer(self.shipping_method).data},
            "products": [{"product": ProductSerializer(product).data, "quantity": 50}],
        }
        self.authorize(self.target.user)
        resp = self.client.patch(f"{self.list_url}{self.target.id}/", data)
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(float(resp.data["total"]), product.price * 50)
