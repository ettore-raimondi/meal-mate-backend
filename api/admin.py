from django.contrib import admin

from .models import FoodRun, MenuItem, Order, Restaurant, User

# Register concrete models so they appear in the Django admin UI.
admin.site.register(User)
admin.site.register(Restaurant)
admin.site.register(MenuItem)
admin.site.register(FoodRun)
admin.site.register(Order)