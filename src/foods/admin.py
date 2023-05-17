from django.contrib import admin
from src.foods.models import Food, FoodCategory

admin.site.register(Food)
admin.site.register(FoodCategory)
