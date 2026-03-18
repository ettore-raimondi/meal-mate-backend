import uuid

from django.conf import settings
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import status, viewsets
import requests
from api.models import Restaurant
from api.serializers import RestaurantSerializer

class RestaurantsViewSet(viewsets.ModelViewSet):
    queryset = Restaurant.objects.all()
    serializer_class = RestaurantSerializer

    @action(detail=False, methods=["get"], url_path="places")
    def get_places(self, request):
        # Get the location from the URL and query google places api for nearby restaurants
        latitude = request.query_params.get("latitude")
        longitude = request.query_params.get("longitude")
        if not latitude or not longitude:
            return Response({"error": "Latitude and longitude parameters are required"}, status=status.HTTP_400_BAD_REQUEST)
        
        api_key = settings.GOOGLE_API_KEY
        fields = [
            'places.displayName',
            'places.location',
            'places.postalAddress',
            'places.id',
            'places.websiteUri',
            'places.internationalPhoneNumber',
        ]
        response = requests.post(
            "https://places.googleapis.com/v1/places:searchNearby", 
            json={
            "includedTypes": ["restaurant"],
            "maxResultCount": 20,
            "locationRestriction": {
                "circle": {
                "center": {
                    "latitude": float(latitude),
                    "longitude": float(longitude)},
                "radius": 500.0
                }
            }
        },
        headers={
            'Content-Type': 'application/json',
            'X-Goog-Api-Key': api_key,
            'X-Goog-FieldMask': ','.join(fields)
        })

        if response.status_code != 200:
            return Response({"error": "Failed to fetch places from Google Places API"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        result = [
            Restaurant(
                id=abs(hash(place.get("id"))), # We need to generate a unique id for each restaurant since these restaurants don't actually exist in our database
                google_places_id=place.get("id"),
                name=place.get("displayName").get("text"),
                address=place.get("postalAddress", {}).get("streetAddress"),
                phone_number=place.get("internationalPhoneNumber"),
                website_url=place.get("websiteUri"),
            )
            for place in response.json().get("places", [])
        ]

        # Django does not actually know how to transform this list of Restaurant objects to JSON, so we need to serialize it first
        serializedData = RestaurantSerializer(result, many=True).data

        return Response(serializedData, status=status.HTTP_200_OK)
        

        
