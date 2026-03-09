from .base import Base
from django.db import models

class Resturant(Base):
    google_places_id = models.IntegerField(blank=False)
    name = models.CharField(max_length=250)
    address = models.CharField(max_length=250)
    phone_number = models.CharField(max_length=20)
    description = models.TextField(blank=True)