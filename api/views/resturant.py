from rest_framework import viewsets
from api.models import Resturant
from api.serializers import ResturantSerializer

class ResturantsViewSet(viewsets.ModelViewSet):
    queryset = Resturant.objects.all()
    serializer_class = ResturantSerializer