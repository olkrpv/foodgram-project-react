from django.contrib import admin

from .models import Ingredient, Tag, Recipe, RecipeIngredient, Follow, Favorite, ShoppingList


class RecipeIngredientInLine(admin.TabularInline):
    model = RecipeIngredient
    extra = 0


class RecipeAdmin(admin.ModelAdmin):
    list_display = ('name', 'author')
    list_filter = ('author', 'name', 'tags')
    inlines = (RecipeIngredientInLine,)
    filter_horizontal = ('tags',)


class IngredientAdmin(admin.ModelAdmin):
    list_display = ('name', 'measurement_unit')
    list_filter = ('name',)


admin.site.register(Ingredient, IngredientAdmin)
admin.site.register(Tag)
admin.site.register(Recipe, RecipeAdmin)
admin.site.register(RecipeIngredient)
admin.site.register(Follow)
admin.site.register(Favorite)
admin.site.register(ShoppingList)
