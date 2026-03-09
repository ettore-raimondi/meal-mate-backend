from .base import Base
from .resturant import Resturant
from django.db import models
from django.conf import settings

class FoodRun(Base):
    organizer = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="organized_food_runs"
    )
    resturant = models.ForeignKey(Resturant, on_delete=models.CASCADE, related_name="food_runs")
    description = models.TextField(blank=True)
    deadline = models.DateTimeField(blank=False)
