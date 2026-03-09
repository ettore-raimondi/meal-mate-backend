from .base import Base
from .resturant import Resturant
from django.db import models

class MenuItem(Base):
    resturant = models.ForeignKey(Resturant, on_delete=models.CASCADE, related_name="menu_items")
    name = models.CharField(max_length=250, blank=False)
    description = models.TextField(blank=True)
    price = models.FloatField(blank=False)
    image_url = models.URLField(blank=True)