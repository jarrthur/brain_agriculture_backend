from decimal import Decimal

from django.db import models
from django.utils.translation import gettext_lazy as _

from core.managers import EstadoManager, FazendaQuerySet
from core.validators import (
    validate_cnpj,
    validate_cpf,
    CnpjOrCpfRequiredValidationError,
    CnpAndCnpjValidationError,
)


class Cidade(models.Model):
    nome = models.CharField(max_length=100)
    estado = models.ForeignKey("core.Estado", on_delete=models.CASCADE)

    def __str__(self):
        return self.nome


class Estado(models.Model):
    nome = models.CharField(max_length=100)
    sigla = models.CharField(max_length=15, unique=True)
    objects = EstadoManager()

    def __str__(self):
        return self.nome

    def natural_key(self):
        return (self.sigla,)


class Cultura(models.Model):
    INITIAL_CULTURAS = [
        "Soja",
        "Milho",
        "Algodão",
        "Café",
        "Cana de Açúcar",
    ]

    nome = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.nome


class Fazenda(models.Model):
    AREA_FIELDS = [
        "area_total_hectares",
        "area_agricultavel_hectares",
        "area_vegetacao_hectares",
    ]
    nome = models.CharField(max_length=100)
    cidade = models.ForeignKey("Cidade", on_delete=models.CASCADE)
    area_total_hectares = models.DecimalField(
        _("Área total em hectares da fazenda"), max_digits=10, decimal_places=2
    )
    area_agricultavel_hectares = models.DecimalField(
        _("Área agricultável em hectares"), max_digits=10, decimal_places=2
    )
    area_vegetacao_hectares = models.DecimalField(
        _("Área de vegetação em hectares"), max_digits=10, decimal_places=2
    )
    culturas_plantadas = models.ManyToManyField("Cultura", related_name="fazendas")
    objects = FazendaQuerySet.as_manager()

    def __str__(self):
        return self.nome

    @staticmethod
    def is_area_agricultavel_and_vegetacao_maior_than_total(
        area_agricultavel_hectares: Decimal,
        area_vegetacao_hectares: Decimal,
        area_total_hectares: Decimal,
    ) -> bool:
        return (
            area_agricultavel_hectares + area_vegetacao_hectares > area_total_hectares
        )


class ProdutorRural(models.Model):
    nome = models.CharField(max_length=100)
    cnpj = models.CharField(
        _("CNPJ"),
        max_length=14,
        unique=True,
        null=True,
        blank=True,
        default=None,
        validators=[validate_cnpj],
    )
    cpf = models.CharField(
        _("CPF"),
        max_length=11,
        unique=True,
        null=True,
        blank=True,
        default=None,
        validators=[validate_cpf],
    )
    fazenda = models.ForeignKey(Fazenda, on_delete=models.CASCADE)
    # identificador = models.CharField(
    #     _("Identificador"),
    #     max_length=14,
    #     unique=True,
    # )
    # tipo = models.CharField(
    #     _("Tipo de Produtor Rural"),
    #     max_length=1,
    #     choices=[(PESSOA_FISICA, "Física"), (PESSOA_JURIDICA, "Jurídica")],
    # )
    #
    # localizacao = models.PointField()
    # limites = models.PolygonField()

    class Meta:
        verbose_name = _("Produtor Rural")
        verbose_name_plural = _("Produtores Rurais")

    def __str__(self):
        return self.nome

    def clean(self):
        if self.cnpj and self.cpf:
            raise CnpAndCnpjValidationError()

        if not self.cnpj and not self.cpf:
            raise CnpjOrCpfRequiredValidationError()

    @staticmethod
    def format_identificador_save_class(identificador: str) -> str:
        return identificador.replace(".", "").replace("-", "").replace("/", "")

    def format_exibicao(self) -> str:
        if self.is_pessoa_juridica():
            return self.format_cnpj()
        return self.format_cpf()

    def is_pessoa_juridica(self) -> bool:
        return bool(self.cnpj)

    def is_pessoa_fisica(self) -> bool:
        return bool(self.cpf)

    def format_cnpj(self) -> str:
        return f"{self.cnpj[0:2]}.{self.cnpj[2:5]}.{self.cnpj[5:8]}/{self.cnpj[8:12]}-{self.cnpj[12:14]}"

    def format_cpf(self) -> str:
        return f"{self.cpf[:3]}.{self.cpf[3:6]}.{self.cpf[6:9]}-{self.cpf[9:]}"
