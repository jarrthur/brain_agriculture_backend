from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework.views import APIView

from django.db import models
from django.db.models import Prefetch

from core.api.serializers import ProdutorRuralSerializer
from core.models import Cultura, Fazenda, ProdutorRural


class ProdutorRuralViewSet(viewsets.ModelViewSet):
    queryset = ProdutorRural.objects.all()
    serializer_class = ProdutorRuralSerializer

    def get_queryset(self):
        prefetch_fazenda_culturas = Prefetch(
            "fazenda__culturas_plantadas", queryset=Cultura.objects.all()
        )
        return (
            super()
            .get_queryset()
            .select_related("fazenda")
            .prefetch_related(prefetch_fazenda_culturas)
        )


class FazendaGraphicsApiView(APIView):
    def get(self, request, format=None):
        total_fazendas_por_estado = Fazenda.objects.total_fazendas_por_estado()
        total_fazenda_culturas = Cultura.objects.annotate(
            total=models.Count("fazendas")
        ).values("nome", "total")
        total_area_agricultavel = Fazenda.objects.aggregate(
            total_agricultavel=models.Sum("area_agricultavel_hectares"),
            total_vegetacao=models.Sum("area_vegetacao_hectares"),
            total_hectares=models.Sum("area_total_hectares"),
            total_fazendas=models.Count("id"),
        )
        total_hectares = total_area_agricultavel.pop("total_hectares")
        total_fazendas = total_area_agricultavel.pop("total_fazendas")

        return Response(
            {
                "total_fazendas": total_fazendas,
                "total_hectares": total_hectares,
                "total_area_agricultavel": total_area_agricultavel,
                "total_fazenda_culturas": total_fazenda_culturas,
                "total_fazendas_por_estado": total_fazendas_por_estado,
            }
        )
