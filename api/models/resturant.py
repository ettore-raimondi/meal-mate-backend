from .base import Base
from django.db import models

class Resturant(Base):
    google_places_id = models.IntegerField(blank=False) # This will be used in the future, just realized this is a paid service
    name = models.CharField(max_length=250)
    address = models.CharField(max_length=250)
    phone_number = models.CharField(max_length=20)
    website_url = models.URLField(blank=True)
    description = models.TextField(blank=True)