from .base import Base
from .restaurant import Restaurant
from django.db import models

class MenuItem(Base):
    restaurant = models.ForeignKey(Restaurant, on_delete=models.CASCADE, related_name="menu_items")
    name = models.CharField(max_length=250, blank=False)
    description = models.TextField(blank=True)
    price = models.FloatField(blank=False)
    image_url = models.URLField(blank=True)