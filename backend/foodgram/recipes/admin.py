from django.contrib import admin

from .models import Ingredient, Tag, Recipe, RecipeIngredient, Follow, Favorite, ShoppingList

admin.site.register(Ingredient)
admin.site.register(Tag)
admin.site.register(Recipe)
admin.site.register(RecipeIngredient)
admin.site.register(Follow)
admin.site.register(Favorite)
admin.site.register(ShoppingList)
