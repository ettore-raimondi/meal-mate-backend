from rest_framework.routers import DefaultRouter

from .user import UsersViewSet
from .restaurant import RestaurantsViewSet
from .food_run import FoodRunViewSet
from .menu_item import MenuItemViewSet
from .order import OrderViewSet

router = DefaultRouter()
router.register(r"users", UsersViewSet)
router.register(r"restaurants", RestaurantsViewSet)
router.register(r"food_runs", FoodRunViewSet)
router.register(r"menu_items", MenuItemViewSet)
router.register(r"orders", OrderViewSet)

__all__ = [
    "router",
    "UsersViewSet",
    "RestaurantsViewSet",
    "FoodRunViewSet",
    "MenuItemViewSet",
    "OrderViewSet",
]