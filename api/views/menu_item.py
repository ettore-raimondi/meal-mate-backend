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
    
    @action(
        detail=False,
        methods=["get"],
        url_path=r"restaurant/(?P<restaurant_id>[^/.]+)",
        name="Get menu items for restaurant",
    )
    def get_menu_items_for_restaurant(self, request, restaurant_id: int) -> Response:
        menu_items = MenuItem.objects.filter(restaurant_id=restaurant_id)
        serializedMenuItems = MenuItemSerializer(menu_items, many=True).data
        return Response(serializedMenuItems, status=status.HTTP_200_OK)
    
    @action(detail=False, methods=["post"], url_path="bulk_create", name="Add many menu items for restaurant")
    def add_menu_items_for_restaurant(self, request) -> list[MenuItem]:
        restaurant_id = request.data.get("restaurant_id")
        menu_items_data = request.data.get("menu_items")

        if not restaurant_id or menu_items_data is None:
            return Response({"error": "Restaurant ID and menu items data are required"}, status=status.HTTP_400_BAD_REQUEST)
        if not isinstance(menu_items_data, list) or len(menu_items_data) == 0:
            return Response({"error": "Send at least one menu item"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            restaurant = Restaurant.objects.get(id=restaurant_id)
        except Restaurant.DoesNotExist:
            return Response({"error": "Restaurant not found"}, status=status.HTTP_404_NOT_FOUND)

        serializer = MenuItemSerializer(
            data=menu_items_data,
            many=True,
            context={"restaurant": restaurant},
        )
        serializer.is_valid(raise_exception=True)
        created_menu_items = serializer.save(restaurant=restaurant)
        return Response(
            MenuItemSerializer(created_menu_items, many=True).data,
            status=status.HTTP_201_CREATED,
        )
        
    @action(detail=False, methods=["patch"], url_path="bulk_update", name="Update menu items for restaurant")
    def update_menu_items_for_restaurant(self, request, pk=None) -> list[MenuItem]:
        restaurant_id = request.data.get("restaurant_id")
        menu_items_data = request.data.get("menu_items")

        if not restaurant_id or menu_items_data is None:
            return Response({"error": "Restaurant ID and menu items data are required"}, status=status.HTTP_400_BAD_REQUEST)
        if not isinstance(menu_items_data, list) or len(menu_items_data) == 0:
            return Response({"error": "Send at least one menu item"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            restaurant = Restaurant.objects.get(id=restaurant_id)
        except Restaurant.DoesNotExist:
            return Response({"error": "Restaurant not found"}, status=status.HTTP_404_NOT_FOUND)

        serializer = MenuItemSerializer(
            MenuItem.objects.filter(restaurant=restaurant),
            data=menu_items_data,
            many=True,
            partial=True,
            context={"restaurant": restaurant},
        )
        serializer.is_valid(raise_exception=True)
        updated_menu_items = serializer.save()
        return Response(
            MenuItemSerializer(updated_menu_items, many=True).data,
            status=status.HTTP_200_OK,
        )