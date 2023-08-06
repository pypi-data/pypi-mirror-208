import random
from copy import deepcopy

from django.urls import reverse
from mixer.backend.django import mixer

from drf_shop_api.products.constants import Units
from drf_shop_api.products.models import (
    Product,
    ProductCategory,
    ProductComment,
    ProductImage,
    ProductProperty,
    Property,
)
from drf_shop_api.products.serializers import ProductSerializer, PropertySerializer
from drf_shop_api.tests import BaseAPITest


class TestProduct(BaseAPITest):
    def setUp(self):
        self.product_count: int = 10
        self.list_url: str = reverse("products:products-list")
        self.screen_size = mixer.blend(Property, title="Screen size", unit=Units.INCH.name)
        self.height = mixer.blend(Property, title="Height", unit=Units.CENTIMETER.name)
        self.electronic = mixer.blend(ProductCategory, title="Electronic")
        self.kitchen = mixer.blend(ProductCategory, title="Kitchen")
        properties = [self.screen_size] * 5 + [self.height] * 5
        categories = [self.electronic] * 5 + [self.kitchen] * 5
        for number, prop, category in zip(range(self.product_count), properties, categories):
            _ = mixer.blend(Product, price=(number + 1) * 10, category=category)
            mixer.blend(ProductImage, product=_, is_main=True)
            mixer.blend(ProductProperty, product=_, property=prop, value=(number + 1) * 10)
        self.target = Product.objects.first()

    def test_list_products(self):
        resp = self.client.get(self.list_url)
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.data["count"], self.product_count)

    def test_list_products_custom_page_size(self):
        qty = 5
        resp = self.client.get(f"{self.list_url}?page_size={qty}")
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(len(resp.data["results"]), qty)

    def test_list_products_custom_page_size_and_page(self):
        qty = 6
        page_count = self.product_count - qty
        resp = self.client.get(f"{self.list_url}?page=2&page_size={qty}")
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(len(resp.data["results"]), page_count)

    def test_detail_product(self):
        resp = self.client.get(f"{self.list_url}{self.target.id}/")
        self.assertEqual(resp.status_code, 200)
        self.assertTrue(all(key in resp.data for key in list(ProductSerializer.Meta.fields)))

    def test_product_filtering_by_title(self):
        resp = self.client.get(f"{self.list_url}?title={self.target.title}")
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.data["results"][0]["id"], self.target.id)
        self.assertEqual(resp.data["count"], 1)

    def test_product_filtering_by_max_price(self):
        resp = self.client.get(f"{self.list_url}?price_max=50")
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.data["count"], 5)

    def test_product_filtering_by_price_range(self):
        resp = self.client.get(f"{self.list_url}?price_max=50&price_min=40")
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.data["count"], 2)

    def test_product_filtering_category(self):
        resp = self.client.get(f"{self.list_url}?category={self.kitchen.url}")
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.data["count"], self.product_count / 2)


class TestProductComment(BaseAPITest):
    def setUp(self):
        self.user = self.create_and_login(is_staff=False)
        self.comment_count: int = 5
        self.list_url = reverse("products:comments-list")
        self.screen_size = mixer.blend(Property, title="Screen size", unit=Units.INCH.name)
        self.height = mixer.blend(Property, title="Height", unit=Units.CENTIMETER.name)
        self.product = mixer.blend(Product, price=mixer.RANDOM)
        mixer.blend(ProductImage, product=self.product, is_main=True)
        mixer.blend(ProductProperty, product=self.product, property=self.screen_size, value=30)
        for _ in range(self.comment_count):
            mixer.blend(ProductComment, product=self.product, user=self.user)
        self.target = ProductComment.objects.first()
        self.data = {"product": self.product.id, "content": "This product is awesome"}

    def test_list_comments(self):
        resp = self.client.get(self.list_url)
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.data["count"], self.comment_count)

    def test_detail_comment(self):
        resp = self.client.get(f"{self.list_url}{self.target.id}/")
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.data["id"], self.target.id)

    def test_create_comment(self):
        resp = self.client.post(self.list_url, self.data)
        self.assertEqual(resp.status_code, 201)
        for key, value in self.data.items():
            self.assertTrue(key in resp.data and resp.data[key] == value)

    def test_create_comment_wrong_product_id(self):
        data = deepcopy(self.data)
        data["product"] = 0
        resp = self.client.post(self.list_url, data)
        self.assertEqual(resp.status_code, 400)

    def test_create_comment_non_authorized(self):
        self.logout()
        resp = self.client.post(self.list_url, self.data)
        self.assertEqual(resp.status_code, 401)

    def test_update_own_comment(self):
        data = deepcopy(self.data)
        data["content"] = "New content"
        resp = self.client.patch(f"{self.list_url}{self.target.id}/", data)
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(ProductComment.objects.get(id=self.target.id).content, "New content")

    def test_update_another_user_comment(self):
        self.create_and_login(email="another_user@example.com")
        data = deepcopy(self.data)
        data["content"] = "New content"
        resp = self.client.patch(f"{self.list_url}{self.target.id}/", data)
        self.assertEqual(resp.status_code, 403)


class TestProperties(BaseAPITest):
    def setUp(self):
        self.prop_count = 10
        self.list_url = reverse("products:properties-list")
        for _ in range(self.prop_count):
            mixer.blend(Property, title=mixer.RANDOM, unit=random.choice(list(Units.__members__)))
        self.target = Property.objects.first()

    def test_list_properties(self):
        resp = self.client.get(self.list_url)
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.data["count"], self.prop_count)

    def test_list_properties_custom_page_size(self):
        qty = 5
        resp = self.client.get(f"{self.list_url}?page_size={qty}")
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(len(resp.data["results"]), qty)

    def test_list_properties_custom_page_size_and_page(self):
        qty = 6
        page_count = self.prop_count - qty
        resp = self.client.get(f"{self.list_url}?page=2&page_size={qty}")
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(len(resp.data["results"]), page_count)

    def test_detail_property(self):
        resp = self.client.get(f"{self.list_url}{self.target.id}/")
        self.assertEqual(resp.status_code, 200)
        self.assertTrue(all(key in resp.data for key in list(PropertySerializer.Meta.fields)))

    def test_property_filtering_by_title(self):
        target = Property.objects.first()
        resp = self.client.get(f"{self.list_url}?title={target.title}")
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.data["results"][0]["id"], target.id)
        self.assertEqual(resp.data["count"], 1)

    def test_property_filtering_by_unit(self):
        resp = self.client.get(f"{self.list_url}?unit={self.target.unit}")
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.data["results"][0]["id"], self.target.id)
