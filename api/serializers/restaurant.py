from api.models import Restaurant
from rest_framework import serializers

class RestaurantSerializer(serializers.ModelSerializer):
    class Meta:
        model = Restaurant
        fields = ['google_places_id', 'name', 'address', 'phone_number', 'description', 'website_url']