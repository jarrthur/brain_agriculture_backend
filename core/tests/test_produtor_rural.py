from parameterized import parameterized
from rest_framework import status, test

from django.core.exceptions import ValidationError as DjangoValidationError
from django.db import IntegrityError
from django.urls import reverse

from core import validators
from core.api.serializers import ProdutorRuralSerializer
from core.models import Fazenda, ProdutorRural
from core.tests.base import BaseCoreTestCase, CoreTestMixin
from users.models import User


class ProdutorRuralModelTestCase(BaseCoreTestCase):
    def setUp(self):
        self.cpf = "12345678909"
        self.cnpj = "40993392000151"
        self.nome_produtor = "Produtor Rural Teste"

    def test_invalid_cnpj(self):
        invalidates_cnpjs = ["15.645.628/1531-56", "12345678123456", "12345678"]
        for cnpj in invalidates_cnpjs:
            with self.subTest(cnpj=cnpj):
                self.assertFalse(validators.validate_cnpj(cnpj))

    def test_invalid_cpf(self):
        invalidate_cpfs = ["123.456.789-10", "12345678910"]
        for cpf in invalidate_cpfs:
            with self.subTest(cpf=cpf):
                with self.assertRaises(DjangoValidationError):
                    validators.validate_cpf(cpf)

    def test_clean_if_cnpj_and_cpf_raises_error(self):
        produtor = ProdutorRural(cnpj=self.cnpj, cpf=self.cpf)
        with self.assertRaises(validators.CnpAndCnpjValidationError):
            produtor.clean()

    def test_clean_if_cnpj_or_cpf_raises_error(self):
        produtor = ProdutorRural()
        with self.assertRaises(validators.CnpjOrCpfRequiredValidationError):
            produtor.clean()

    def test_unique_cpf(self):
        self.create_produtor_rural(cpf=self.cpf, nome=self.nome_produtor)
        with self.assertRaises(IntegrityError):
            self.create_produtor_rural(cpf=self.cpf, nome=self.nome_produtor)

    def test_unique_cnpj(self):
        self.create_produtor_rural(cnpj=self.cnpj, nome=self.nome_produtor)
        with self.assertRaises(IntegrityError):
            self.create_produtor_rural(cnpj=self.cnpj, nome=self.nome_produtor)

    def test_str(self):
        produtor = self.create_produtor_rural(cpf=self.cpf, nome=self.nome_produtor)
        self.assertEqual(str(produtor), self.nome_produtor)

    def test_format_cpf(self):
        produtor = ProdutorRural(cpf=self.cpf, nome=self.nome_produtor)
        self.assertEqual(produtor.format_cpf(), "123.456.789-09")

    def test_format_cnpj(self):
        produtor = ProdutorRural(cnpj=self.cnpj, nome=self.nome_produtor)
        self.assertEqual(produtor.format_cnpj(), "40.993.392/0001-51")

    def test_is_pessoa_fisica(self):
        produtor = ProdutorRural(cpf=self.cpf, nome=self.nome_produtor)
        self.assertTrue(produtor.is_pessoa_fisica())

    def test_is_pessoa_juridica(self):
        produtor = ProdutorRural(cnpj=self.cnpj, nome=self.nome_produtor)
        self.assertTrue(produtor.is_pessoa_juridica())

    def test_produtor_rural_and_fazenda_relacao(self):
        nome_fazenda = "Fazenda Teste 2"
        fazenda = self.create_fazenda(
            cidade=self.create_cidade(self.create_estado()),
            nome=nome_fazenda,
        )
        produtor = self.create_produtor_rural(
            cpf=self.cpf, nome=self.nome_produtor, fazenda=fazenda
        )
        self.assertEqual(produtor.fazenda.nome, nome_fazenda)


class TestProdutorRuralSerializer(BaseCoreTestCase):
    def setUp(self):
        self.cpf = "12345678909"
        self.cnpj = "40993392000151"
        self.data = self.create_produtor_rural_data()

    @parameterized.expand(
        [
            ("123.456.789-09", "", True),  # CPF válido, CNPJ vazio, esperado válido
            ("", "12.345.678/0001-95", True),  # CPF vazio, CNPJ válido, esperado válido
            (
                "123.456.789-09",
                "12.345.678/0001-95",
                False,
            ),  # Ambos preenchidos, esperado inválido
            ("", "", False),  # Ambos vazios, esperado inválido
            ("123.456.789-10", "", False),  # CPF incorreto, esperado inválido
        ]
    )
    def test_cpf_cnpj_validations(self, cpf, cnpj, valido):
        self.data["cpf"] = cpf
        self.data["cnpj"] = cnpj
        serializer = ProdutorRuralSerializer(data=self.data)
        self.assertEqual(serializer.is_valid(), valido)


class TestProdutorViewSet(CoreTestMixin, test.APITestCase):
    def setUp(self):
        self.user = User.objects.create(email="email@email.com", password="password")
        self.client.force_authenticate(user=self.user)

    def test_list_produtor_rural(self):
        produtor_rural = self.create_produtor_rural()
        url = reverse("core:produtor-rural-list")
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

        data_esperada = ProdutorRuralSerializer(produtor_rural).data
        self.assertEqual(response.data[0], data_esperada)

    def test_retrieve_produtor_rural(self):
        nome_produtor_rural = "Produtor Rural Teste"
        produtor_rural = self.create_produtor_rural(nome=nome_produtor_rural)
        url = reverse("core:produtor-rural-detail", kwargs={"pk": produtor_rural.pk})
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["nome"], nome_produtor_rural)

    def test_create_produtor_rural(self):
        data = self.create_produtor_rural_data()
        url = reverse("core:produtor-rural-list")
        response = self.client.post(url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["cpf"], data["cpf"])
        self.assertEqual(ProdutorRural.objects.count(), 1)
        self.assertEqual(Fazenda.objects.count(), 1)
        self.assertEqual(ProdutorRural.objects.first().nome, "Produtor Rural Teste 2")

    def test_patch_produtor_rural(self):
        produtor_rural = self.create_produtor_rural()
        novo_nome_produtor = "Produtor Rural Teste 3"
        data = {"nome": novo_nome_produtor}
        url = reverse("core:produtor-rural-detail", kwargs={"pk": produtor_rural.pk})
        response = self.client.patch(url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["nome"], novo_nome_produtor)
        self.assertEqual(ProdutorRural.objects.first().nome, novo_nome_produtor)

    @parameterized.expand(
        [
            (100, 51, 51),  # Passando os valores de data já inválidos. 51 + 51 = 102
            ("", 50, 51),  # Instância de fazenda com área total de 100. 50 + 51 = 101
            (
                100,
                "",
                51,
            ),  # Instância de fazenda com área agricultável de 80. 51 + 80 = 131
            (
                100,
                90,
                "",
            ),  # Instância de fazenda com área de vegetação de 20. 90 + 20 = 110
        ]
    )
    def test_patch_produtor_rural_com_area_fields_invalida(
        self, area_total_hectares, area_agricultavel_hectares, area_vegetacao_hectares
    ):
        produtor_rural = self.create_produtor_rural()
        url = reverse("core:produtor-rural-detail", kwargs={"pk": produtor_rural.pk})
        data = {"fazenda": {}}
        area_fields = {
            "area_total_hectares": area_total_hectares,
            "area_agricultavel_hectares": area_agricultavel_hectares,
            "area_vegetacao_hectares": area_vegetacao_hectares,
        }
        data["fazenda"].update(
            {field: value for field, value in area_fields.items() if value}
        )
        response = self.client.patch(url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        # Caso todos os campos de área venha no request,
        # o erro é disparo por FazendaSerializer (response.data.fazenda.non_field_errors)
        response_non_field_errors = (
            response.data["fazenda"]["non_field_errors"][0]
            if "fazenda" in response.data
            else response.data.get("non_field_errors")[0]
        )
        self.assertEqual(
            response_non_field_errors,
            validators.AreaHectaresValidationError.default_detail,
        )

    def test_delete_produtor_rural(self):
        produtor_rural = self.create_produtor_rural()
        url = reverse("core:produtor-rural-detail", kwargs={"pk": produtor_rural.pk})
        response = self.client.delete(url)

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(ProdutorRural.objects.count(), 0)
        self.assertEqual(Fazenda.objects.count(), 1)

    def test_put_produtor_rural_com_nome_fazenda_diferente(self):
        produtor_rural = self.create_produtor_rural()
        novo_nome_fazenda = "Novo nome de fazenda"
        fazenda_data_com_novo_nome = {
            "fazenda": {
                "nome": novo_nome_fazenda,
                "cidade": produtor_rural.fazenda.cidade_id,
                "area_total_hectares": 100.0,
                "area_agricultavel_hectares": 80.0,
                "area_vegetacao_hectares": 20.0,
                "culturas_plantadas": produtor_rural.fazenda.culturas_plantadas.values_list(
                    "id", flat=True
                ),
            }
        }
        data = self.create_produtor_rural_data(**fazenda_data_com_novo_nome)
        url = reverse("core:produtor-rural-detail", kwargs={"pk": produtor_rural.pk})
        response = self.client.put(url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["fazenda"]["nome"], novo_nome_fazenda)
        self.assertEqual(Fazenda.objects.first().nome, novo_nome_fazenda)

    # TODO: Testar invalidação em put e patch de um produtor rural pessoa fisíca com cnpj
