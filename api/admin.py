from django.contrib import admin

from .models import FoodRun, MenuItem, Order, Resturant, User

# Register concrete models so they appear in the Django admin UI.
admin.site.register(User)
admin.site.register(Resturant)
admin.site.register(MenuItem)
admin.site.register(FoodRun)
admin.site.register(Order)