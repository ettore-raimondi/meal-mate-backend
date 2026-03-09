from api.models import Resturant
from rest_framework import serializers

class ResturantSerializer(serializers.ModelSerializer):
    class Meta:
        model = Resturant
        fields = ['google_places_id', 'name', 'address', 'phone_number', 'description']