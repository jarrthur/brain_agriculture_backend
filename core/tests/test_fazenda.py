from unittest.mock import patch
from rest_framework import status
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response
from rest_framework.test import APITestCase

from django.contrib.auth import get_user_model
from django.urls import reverse

from core.api.serializers import FazendaSerializer
from core.validators import AreaHectaresValidationError

from .base import BaseCoreTestCase, CoreTestMixin

User = get_user_model()


class FazendaGraphicsApiViewTests(APITestCase, CoreTestMixin):
    def setUp(self):
        self.email = "email@email.com"
        self.password = "password"

    def get_response(self, url=reverse("core:fazenda-graphics"), authenticated=True):
        if authenticated:
            self.user = User.objects.create_user(
                email=self.email, password=self.password
            )
            token = self.obtain_access_token().data["access"]
            self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")
        return self.client.get(url)

    def post_response(self, url, data):
        return self.client.post(url, data, format="json")

    def obtain_access_token(self) -> Response:
        url = reverse("users:token_obtain_pair")
        response = self.post_response(
            url=url, data={"email": self.email, "password": self.password}
        )
        return response

    def test_get_attrs_and_is_authenticated_fazenda_graphics(self):
        response = self.get_response(authenticated=True)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("total_fazendas", response.data)
        self.assertIn("total_hectares", response.data)
        self.assertIn("total_area_agricultavel", response.data)
        self.assertIn("total_fazenda_culturas", response.data)
        self.assertIn("total_fazendas_por_estado", response.data)

    @patch("core.api.views.Fazenda.objects.total_fazendas_por_estado")
    @patch("core.api.views.Cultura.objects.annotate")
    @patch("core.api.views.Fazenda.objects.aggregate")
    def test_check_fazenda_graphics_values(
        self, mock_aggregate, mock_annotate, mock_total_fazendas_por_estado
    ):
        mock_aggregate.return_value = {
            "total_agricultavel": 1000,
            "total_vegetacao": 500,
            "total_hectares": 1500,
            "total_fazendas": 10,
        }
        mock_annotate.return_value.values.return_value = [
            {"nome": "Café", "total": 5},
            {"nome": "Milho", "total": 3},
        ]
        mock_total_fazendas_por_estado.return_value = {
            "Acre": 5,
            "Bahia": 3,
        }

        response = self.get_response()
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["total_fazendas"], 10)
        self.assertEqual(response.data["total_hectares"], 1500)
        self.assertEqual(
            response.data["total_area_agricultavel"]["total_agricultavel"], 1000
        )
        self.assertEqual(
            response.data["total_area_agricultavel"]["total_vegetacao"], 500
        )
        self.assertEqual(len(response.data["total_fazenda_culturas"]), 2)
        self.assertEqual(response.data["total_fazenda_culturas"][0]["nome"], "Café")
        self.assertEqual(response.data["total_fazenda_culturas"][0]["total"], 5)
        self.assertEqual(response.data["total_fazenda_culturas"][1]["nome"], "Milho")
        self.assertEqual(response.data["total_fazenda_culturas"][1]["total"], 3)
        self.assertEqual(len(response.data["total_fazendas_por_estado"]), 2)
        self.assertEqual(response.data["total_fazendas_por_estado"]["Acre"], 5)
        self.assertEqual(response.data["total_fazendas_por_estado"]["Bahia"], 3)


class FazendaSerializerTestCase(BaseCoreTestCase):
    def setUp(self, *args, **kwargs):
        estado = self.create_estado()
        self.data = {
            "nome": "Fazenda Teste",
            "cidade": self.create_cidade(estado=estado).pk,
            "area_total_hectares": 100.0,
            "area_agricultavel_hectares": 80.0,
            "area_vegetacao_hectares": 20.0,
            "culturas_plantadas": [
                self.create_cultura().pk,
                self.create_cultura("Algodão").pk,
            ],
        }

    def test_valid_data(self):
        serializer = FazendaSerializer(data=self.data)
        self.assertTrue(serializer.is_valid())

    def test_soma_area_agricultavel_vegetacao_maior_que_total(self):
        self.data["area_agricultavel_hectares"] = 90.0
        serializer = FazendaSerializer(data=self.data)
        with self.assertRaisesMessage(
            ValidationError, AreaHectaresValidationError.default_detail
        ):
            serializer.is_valid(raise_exception=True)
