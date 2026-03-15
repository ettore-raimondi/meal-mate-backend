from .base import Base
from django.db import models

class Restaurant(Base):
    google_places_id = models.CharField(max_length=128, blank=False)
    name = models.CharField(max_length=250)
    address = models.CharField(max_length=250)
    phone_number = models.CharField(max_length=20)
    website_url = models.URLField(blank=True)
    description = models.TextField(blank=True)