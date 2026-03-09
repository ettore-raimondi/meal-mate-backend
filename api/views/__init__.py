from rest_framework.routers import DefaultRouter

from .user import UsersViewSet
from .resturant import ResturantsViewSet
from .food_run import FoodRunViewSet
from .menu_item import MenuItemViewSet
from .order import OrderViewSet

router = DefaultRouter()
router.register(r"users", UsersViewSet)
router.register(r"resturants", ResturantsViewSet)
router.register(r"food_runs", FoodRunViewSet)
router.register(r"menu_items", MenuItemViewSet)
router.register(r"orders", OrderViewSet)

__all__ = [
    "router",
    "UsersViewSet",
    "ResturantsViewSet",
    "FoodRunViewSet",
    "MenuItemViewSet",
    "OrderViewSet",
]