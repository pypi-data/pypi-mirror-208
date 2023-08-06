from django.apps import apps
from django.conf import settings
from rest_framework.test import APITestCase
from rest_framework_simplejwt.tokens import AccessToken


class BaseAPITest(APITestCase):
    def create(self, email="test@mail.com", password="test_password"):
        user = apps.get_model(f"{settings.AUTH_USER_MODEL}").objects.create_user(email=email, password=password)
        user.is_active = True
        user.save()
        return user

    def create_and_login(self, email="test@mail.com", password="test_password", is_staff=False, is_superuser=False):
        user = self.create(email=email, password=password)
        user.is_staff = is_staff
        user.is_superuser = is_superuser
        user.save()
        self.authorize(user)
        return user

    def authorize(self, user, **additional_headers):
        token = AccessToken.for_user(user)
        self.client.credentials(HTTP_AUTHORIZATION=f"JWT {token}", **additional_headers)

    def logout(self, **additional_headers):
        self.client.credentials(**additional_headers)
