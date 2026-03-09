from .base import Base
from .food_run import FoodRun
from .menu_item import MenuItem
from django.db import models
from django.conf import settings

class Order(Base):
    food_run = models.ForeignKey(
        FoodRun,
        on_delete=models.CASCADE,
        related_name="orders"
    )

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
    )

    menu_item = models.ForeignKey(
        MenuItem,
        on_delete=models.CASCADE,
        related_name="orders"
    )

    note = models.CharField(max_length=250, blank=True)
