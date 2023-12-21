from rest_framework import serializers

from recipes.models import Ingredient, Recipe, User, Follow, Favorite, ShoppingList, Tag


class TagSerializer(serializers.ModelSerializer):

    class Meta:
        model = Tag
        fields = '__all__'
