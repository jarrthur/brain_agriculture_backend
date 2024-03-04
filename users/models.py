from django.contrib.auth.models import AbstractBaseUser
from django.db import models
from django.utils.translation import gettext_lazy as _

from users.managers import UserManager


class User(AbstractBaseUser):
    email = models.EmailField(_("E-mail"), unique=True)
    nome = models.CharField(max_length=100)
    data_registro = models.DateTimeField(_("Data de registro"), auto_now_add=True)

    is_active = models.BooleanField(_("Ativo?"), default=True)
    is_admin = models.BooleanField(_("Administrador?"), default=False)

    EMAIL_FIELD = "email"
    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = [
        "nome",
    ]
    objects = UserManager()

    def __str__(self) -> str:
        return self.nome

    def get_full_name(self) -> str:
        return self.nome

    def get_short_name(self) -> str:
        return self.nome

    def has_perm(self, perm, obj=None) -> bool:
        return True

    def has_module_perms(self, app_label) -> bool:
        return True

    @property
    def is_staff(self):
        return self.is_admin
