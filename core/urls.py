from django.urls import path
from rest_framework import routers

from core.api.views import FazendaGraphicsApiView, ProdutorRuralViewSet

app_name = "core"

router = routers.DefaultRouter()
router.register("produtores-rurais", ProdutorRuralViewSet, basename="produtor-rural")

urlpatterns = [
    path("graphics/", FazendaGraphicsApiView.as_view(), name="fazenda-graphics")
]

urlpatterns += router.urls
