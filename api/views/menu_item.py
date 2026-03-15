from rest_framework import viewsets, status
from api.models import MenuItem, Restaurant
from api.serializers import MenuItemSerializer
from api.services.scraper_service import ScraperService
from rest_framework.decorators import action
from rest_framework.response import Response

class MenuItemViewSet(viewsets.ModelViewSet):
    queryset = MenuItem.objects.all()
    serializer_class = MenuItemSerializer

    @action(detail=False, methods=["get"], url_path="scrape", name="Scrape Menu Items for Restaurant")
    def scrape_menu_items_for_restaurant(self, request) -> list[MenuItem]:
        website_url = request.query_params.get("restaurant_website_url")
        if not website_url:
            return Response({"error": "Restaurant website URL is required"}, status=status.HTTP_400_BAD_REQUEST)

        scraper_service = ScraperService()
        menu_items = scraper_service.menu_scraper(website_url)
        serializedMenuItems = MenuItemSerializer(menu_items, many=True).data
        return Response(serializedMenuItems, status=status.HTTP_200_OK)