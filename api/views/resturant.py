from django.conf import settings
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import status, viewsets
from rest_framework import viewsets
import requests
from api.models import Resturant
from api.serializers import ResturantSerializer

class ResturantsViewSet(viewsets.ModelViewSet):
    queryset = Resturant.objects.all()
    serializer_class = ResturantSerializer

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

        result = [
            {
                "google_places_id": place.get("id"),
                "name": place.get("displayName").get("text"),
                "address": place.get("postalAddress", {}).get("streetAddress"),
                "phone_number": place.get("internationalPhoneNumber"),
                "website_uri": place.get("websiteUri"),
            }
            for place in response.json().get("places", [])
        ]

        return Response(result, status=status.HTTP_200_OK)
        

        
