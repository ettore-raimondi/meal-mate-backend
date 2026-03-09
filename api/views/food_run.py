from rest_framework import viewsets
from api.models import FoodRun
from api.serializers import FoodRunSerializer

class FoodRunViewSet(viewsets.ModelViewSet):
    queryset = FoodRun.objects.all()
    serializer_class = FoodRunSerializer