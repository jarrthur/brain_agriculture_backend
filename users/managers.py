from django.contrib.auth.base_user import BaseUserManager
from django.utils.translation import gettext_lazy as _


class UserManager(BaseUserManager):
    def create_user(self, password, **extra_fields):
        email = extra_fields.get("email")
        if not email:
            raise ValueError(_("E-mail é obrigatório"))
        extra_fields.update({"email": self.normalize_email(email)})
        user = self.model(**extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, password, **extra_fields):
        extra_fields.setdefault("is_admin", True)
        extra_fields.setdefault("is_active", True)

        if extra_fields.get("is_admin") is not True:
            raise ValueError(_("Superuser deve ter is_staff=True."))
        return self.create_user(password, **extra_fields)
