from core.models import Cidade, Cultura, Estado, Fazenda, ProdutorRural
from django.test import TestCase


class CoreTestMixin:
    def create_cidade(self, estado, nome="Cidade Teste"):
        return Cidade.objects.create(nome=nome, estado=estado)

    def create_estado(self, nome="Estado Teste", sigla="ET"):
        estado, _ = Estado.objects.get_or_create(nome=nome, sigla=sigla)
        return estado

    def create_cultura(self, nome="Soja"):
        cultura, _ = Cultura.objects.get_or_create(nome=nome)
        return cultura

    def create_fazenda(self, cidade, culturas_plantadas=None, nome="Fazenda Teste"):
        fazenda = Fazenda.objects.create(
            nome=nome,
            cidade=cidade,
            area_total_hectares=100.0,
            area_agricultavel_hectares=80.0,
            area_vegetacao_hectares=20.0,
        )
        if culturas_plantadas:
            fazenda.culturas_plantadas.set(culturas_plantadas)
        return fazenda

    def create_produtor_rural(
        self, nome="Produtor Rural Teste", cpf="12345678909", cnpj=None, fazenda=None
    ):
        if not fazenda:
            culturas_plantadas = [
                self.create_cultura("Café"),
                self.create_cultura("Cana de Açúcar"),
            ]
            fazenda = self.create_fazenda(
                self.create_cidade(self.create_estado()), culturas_plantadas
            )
        return ProdutorRural.objects.create(
            nome=nome,
            cpf=cpf,
            cnpj=cnpj,
            fazenda=fazenda,
        )

    def create_produtor_rural_data(self, **kwargs):
        estado = self.create_estado()
        cidade = self.create_cidade(estado)
        culturas_plantadas = [
            self.create_cultura("Café").pk,
            self.create_cultura("Cana de Açúcar").pk,
        ]
        data = {
            "nome": "Produtor Rural Teste 2",
            "cpf": "12345678909",
            "fazenda": {
                "nome": "Fazenda Teste 2",
                "cidade": cidade.pk,
                "area_total_hectares": 100.0,
                "area_agricultavel_hectares": 80.0,
                "area_vegetacao_hectares": 20.0,
                "culturas_plantadas": culturas_plantadas,
            },
        }
        data.update(kwargs)
        return data


class BaseCoreTestCase(CoreTestMixin, TestCase):
    pass
