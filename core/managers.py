from django.db import models


class EstadoManager(models.Manager):
    def get_by_natural_key(self, sigla):
        return self.get(sigla=sigla)


class FazendaQuerySet(models.QuerySet):
    def total_fazendas_por_estado(self):
        return self.values("cidade__estado__nome").annotate(total=models.Count("id"))

    def total_fazendas_por_cultura(self):
        return self.values("culturas_plantadas__nome").annotate(
            total=models.Count("id")
        )
