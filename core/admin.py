from django.contrib import admin

from core.models import Cidade, Cultura, Estado, Fazenda, ProdutorRural

# Register your models here.

admin.site.register(ProdutorRural)
admin.site.register(Fazenda)
admin.site.register(Cultura)
admin.site.register(Estado)
admin.site.register(Cidade)
