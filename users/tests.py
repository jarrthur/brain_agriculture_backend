from rest_framework import status
from rest_framework.response import Response
from rest_framework.test import APITestCase
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.exceptions import TokenError

from django.contrib.auth import get_user_model
from django.urls import reverse
from django.test import TestCase

User = get_user_model()


class UserModelTestCase(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.email = "testuser@exemplo.com"
        cls.password = "pass"
        cls.user = User.objects.create_user(email=cls.email, password=cls.password)

    def test_is_active_default_value(self):
        self.assertTrue(self.user.is_active)

    def test_is_admin_default_value(self):
        self.assertIs(self.user.is_admin, False)


class BaseUserViewTestCase(APITestCase):
    @classmethod
    def setUpTestData(cls):
        cls.email = "testuser@exemplo.com"
        cls.password = "pass"
        cls.user = User.objects.create_user(email=cls.email, password=cls.password)

    def post_response(self, url, data={}, authenticated=True):
        if authenticated:
            access_token = self.obtain_access_token().data["access"]
            self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {access_token}")
        return self.client.post(url, data, format="json")

    def obtain_access_token(self) -> Response:
        url = reverse("users:token_obtain_pair")
        response = self.post_response(
            url, {"email": self.email, "password": self.password}, authenticated=False
        )
        return response

    def obtain_refresh_token(self, refresh_token) -> Response:
        url = reverse("users:token_refresh")
        response = self.post_response(
            url, {"refresh": refresh_token}, authenticated=False
        )
        return response


class TokenObtainPairViewTestCase(BaseUserViewTestCase):

    def test_obtain_and_refresh_token(self):
        response = self.obtain_access_token()
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue("access" in response.data)
        self.assertTrue("refresh" in response.data)

        refresh_response = self.obtain_refresh_token(response.data["refresh"])
        self.assertEqual(refresh_response.status_code, status.HTTP_200_OK)
        self.assertTrue("access" in refresh_response.data)


class LogoutViewTests(BaseUserViewTestCase):
    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        cls.logout_url = reverse("users:logout")

    def test_logout_sucesso_and_is_in_blacklist(self):
        refresh_token = RefreshToken.for_user(self.user)
        data = {"refresh_token": str(refresh_token)}
        response = self.post_response(self.logout_url, data)

        self.assertEqual(response.status_code, status.HTTP_205_RESET_CONTENT)
        with self.assertRaises(TokenError):
            self.assertTrue(refresh_token.check_blacklist())

    def test_logout_invalid_token(self):
        # Token vazio
        response = self.post_response(self.logout_url)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data["detail"], "Invalid token")
