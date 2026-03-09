from api.models import FoodRun
from rest_framework import serializers

class FoodRunSerializer(serializers.ModelSerializer):
    class Meta:
        model = FoodRun
        fields = ['id', 'description', 'created_at', 'resturant', 'organizer', 'deadline']