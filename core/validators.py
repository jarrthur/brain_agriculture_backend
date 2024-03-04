import re

from rest_framework import status
from rest_framework.exceptions import ValidationError as DRFValidationError

from django.core.exceptions import ValidationError as DjangoValidationError
from django.utils.translation import gettext_lazy as _


def validate_cnpj(cnpj):
    # Remove caracteres não numéricos
    cnpj = re.sub(r"[^0-9]", "", cnpj)

    # Verifica se o CNPJ possui 14 dígitos
    if len(cnpj) != 14:
        return False

    # Evita CNPJs com todos os números iguais (ex: 11111111111111)
    if cnpj == cnpj[0] * 14:
        return False

    # Calcula e valida o primeiro dígito verificador
    soma = sum([int(cnpj[i]) * int(5 - i if i < 4 else 13 - i) for i in range(12)])
    resto = soma % 11
    if int(cnpj[12]) != (0 if resto < 2 else 11 - resto):
        return False

    # Calcula e valida o segundo dígito verificador
    soma = sum([int(cnpj[i]) * int(6 - i if i < 5 else 14 - i) for i in range(13)])
    resto = soma % 11
    if int(cnpj[13]) != (0 if resto < 2 else 11 - resto):
        return False

    return True


def validate_cpf(value):
    # Remove caracteres não numéricos
    cpf = re.sub("[^0-9]", "", value)

    # Verifica se o CPF tem 11 dígitos
    if len(cpf) != 11:
        raise DjangoValidationError(_("CPF deve ter 11 dígitos."))

    # Verifica se todos os dígitos são iguais
    if cpf == cpf[0] * 11:
        raise DjangoValidationError(_("CPF inválido."))

    # Cálculo dos dígitos verificadores
    for i in range(9, 11):
        valor = sum((int(cpf[num]) * ((i + 1) - num) for num in range(0, i)))
        digito = ((valor * 10) % 11) % 10
        if str(digito) != cpf[i]:
            raise DjangoValidationError(_("CPF inválido."))


class CnpAndCnpjValidationError(DjangoValidationError):
    def __init__(
        self, message="O produtor rural não pode ter CNPJ e CPF ao mesmo tempo"
    ):
        self.message = message
        self.code = "cnpj_and_cpf_error"
        super().__init__(self.message, self.code)


class AreaHectaresValidationError(DRFValidationError):
    default_detail = "A soma de área agrícultável e vegetação não pode ser maior que a área total da fazenda"
    default_code = "area_hectares_total_error"
    status_code = status.HTTP_400_BAD_REQUEST


class CnpjOrCpfRequiredMixin:
    message = "O produtor rural deve ter CNPJ ou CPF"
    code = "cnpj_or_cpf_required_error"
    status_code = status.HTTP_400_BAD_REQUEST


class CnpjOrCpfRequiredValidationError(CnpjOrCpfRequiredMixin, DjangoValidationError):
    def __init__(self):
        super().__init__(self.message, self.code)


class CnpjOrCpfRequiredDRFValidationError(CnpjOrCpfRequiredMixin, DRFValidationError):

    def __init__(self, detail=None, code=None):
        if detail is None:
            detail = self.message
        if code is None:
            code = self.code
        super().__init__(detail, code)
