from django.db import transaction

from base.serializers import BaseModelSerializer
from core.models import Fazenda, ProdutorRural
from core.validators import (
    AreaHectaresValidationError,
    CnpAndCnpjValidationError,
    CnpjOrCpfRequiredDRFValidationError,
)


class FazendaSerializer(BaseModelSerializer):
    class Meta:
        model = Fazenda
        fields = (
            "id",
            "nome",
            "cidade",
            "area_total_hectares",
            "area_agricultavel_hectares",
            "area_vegetacao_hectares",
            "culturas_plantadas",
        )

    def validate(self, attrs: dict) -> dict:
        if all(key in attrs for key in Fazenda.AREA_FIELDS):
            if Fazenda.is_area_agricultavel_and_vegetacao_maior_than_total(
                attrs["area_agricultavel_hectares"],
                attrs["area_vegetacao_hectares"],
                attrs["area_total_hectares"],
            ):
                raise AreaHectaresValidationError()
        return attrs


class ProdutorRuralSerializer(BaseModelSerializer):
    fazenda = FazendaSerializer(required=True)

    class Meta:
        model = ProdutorRural
        fields = ("id", "nome", "cnpj", "cpf", "fazenda")
        extra_kwargs = {
            "cnpj": {"max_length": 18},
            "cpf": {"max_length": 14},
        }

    @transaction.atomic
    def create(self, validated_data: dict) -> ProdutorRural:
        fazenda_data = validated_data.pop("fazenda")
        cultura_data = fazenda_data.pop("culturas_plantadas")
        fazenda = Fazenda.objects.create(**fazenda_data)
        fazenda.culturas_plantadas.set(cultura_data)
        produtor_rural = ProdutorRural.objects.create(**validated_data, fazenda=fazenda)
        return produtor_rural

    def update(self, instance: ProdutorRural, validated_data: dict) -> ProdutorRural:
        fazenda_data = validated_data.pop("fazenda", None)
        if fazenda_data:
            fazenda = instance.fazenda
            cultura_data = fazenda_data.pop("culturas_plantadas", None)
            for attr, value in fazenda_data.items():
                setattr(fazenda, attr, value)
            fazenda.save()
            if cultura_data:
                fazenda.culturas_plantadas.set(cultura_data)
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        return instance

    def is_cnpj_and_cpf_data_or_cpf_and_cnpj_data(self, cpf: str, cnpj: str) -> bool:
        return self.instance and bool(
            (self.instance.cnpj and cpf) or (cnpj and self.instance.cpf)
        )

    def validate(self, attrs: dict) -> dict:
        cnpj = attrs.get("cnpj")
        cpf = attrs.get("cpf")
        patch_method = (
            "request" in self.context and self.context["request"].method == "PATCH"
        )
        if (cnpj and cpf) or self.is_cnpj_and_cpf_data_or_cpf_and_cnpj_data(cpf, cnpj):
            raise CnpAndCnpjValidationError()

        if not (cnpj or cpf) and not patch_method:
            raise CnpjOrCpfRequiredDRFValidationError()

        if self.instance and patch_method:
            # Validação necessária caso o método seja PATCH para mesclar os dados
            # do request com os dados da instância de fazenda
            instance_fazenda_area_and_data = self.merge_fazenda_area_data(attrs)
            if Fazenda.is_area_agricultavel_and_vegetacao_maior_than_total(
                **instance_fazenda_area_and_data
            ):
                raise AreaHectaresValidationError()

        return attrs

    def merge_fazenda_area_data(self, data: dict) -> dict:
        fazenda_data = data.get("fazenda", {})
        fazenda = self.instance.fazenda
        fazenda_instance_data = {}
        for key in Fazenda.AREA_FIELDS:
            fazenda_instance_data[key] = fazenda_data.get(key, getattr(fazenda, key))
        return fazenda_instance_data

    def to_internal_value(self, data):
        # Limpando pontuação de CPF e CNPJ para o serializer validar unicidade,
        # ao invés de utilzar em def validade_<campo>() para manter padronização dos dados
        data = data.copy()
        cpf = data.get("cpf")
        cnpj = data.get("cnpj")
        if cpf:
            data["cpf"] = ProdutorRural.format_identificador_save_class(cpf)
        if cnpj:
            data["cnpj"] = ProdutorRural.format_identificador_save_class(cnpj)
        return super().to_internal_value(data)
