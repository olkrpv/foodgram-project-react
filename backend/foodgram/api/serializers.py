from rest_framework import serializers

from recipes.models import Ingredient, Recipe, Tag, RecipeIngredient, Follow, Favorite, ShoppingList
from users.models import CustomUser


class UserSerializer(serializers.ModelSerializer):
    is_subscribed = serializers.SerializerMethodField()

    class Meta:
        model = CustomUser
        fields = ('email', 'id', 'username', 'first_name', 'last_name', 'is_subscribed')

    def get_is_subscribed(self, obj):
        current_user = self.context['request'].user
        if current_user.is_anonymous:
            return False
        return Follow.objects.filter(user=current_user, following=obj).exists()


class TagSerializer(serializers.ModelSerializer):

    class Meta:
        model = Tag
        fields = '__all__'


class IngredientSerializer(serializers.ModelSerializer):

    class Meta:
        model = Ingredient
        fields = '__all__'


class RecipeIngredientSerializer(serializers.ModelSerializer):
    name = serializers.StringRelatedField(source='ingredient.name')
    measurement_unit = serializers.StringRelatedField(
        source='ingredient.measurement_unit'
    )
    id = serializers.PrimaryKeyRelatedField(source='ingredient.id', read_only=True)

    class Meta:
        model = RecipeIngredient
        fields = ('id', 'name', 'measurement_unit', 'amount')


class RecipeListDetailSerializer(serializers.ModelSerializer):
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()
    tags = TagSerializer(many=True)
    author = UserSerializer(read_only=True)
    ingredients = serializers.SerializerMethodField()

    class Meta:
        model = Recipe
        fields = (
            'id', 'tags', 'author', 'ingredients', 'is_favorited',
            'is_in_shopping_cart', 'name', 'image', 'text', 'cooking_time'
        )

    def get_ingredients(self, obj):
        return RecipeIngredientSerializer(
            RecipeIngredient.objects.filter(recipe=obj).all(), many=True
        ).data

    def is_item_in_list(self, obj, list_model):
        current_user = self.context['request'].user
        if current_user.is_anonymous:
            return False
        return list_model.objects.filter(user=current_user, recipe=obj).exists()

    def get_is_favorited(self, obj):
        return self.is_item_in_list(obj, Favorite)

    def get_is_in_shopping_cart(self, obj):
        return self.is_item_in_list(obj, ShoppingList)
