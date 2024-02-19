import base64

from django.core.files.base import ContentFile

from rest_framework import serializers, status
from rest_framework.validators import UniqueTogetherValidator

from recipes.models import (
    Favorite,
    Follow,
    Ingredient,
    Recipe,
    RecipeIngredient,
    ShoppingList,
    Tag,
    User
)


class UserSerializer(serializers.ModelSerializer):
    is_subscribed = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = (
            'email', 'id', 'username',
            'first_name', 'last_name', 'is_subscribed'
        )

    def get_is_subscribed(self, obj):
        current_user = self.context['request'].user
        return (
            current_user.is_authenticated
            and Follow.objects.filter(user=current_user, following=obj).exists()
        )


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
    id = serializers.PrimaryKeyRelatedField(
        source='ingredient.id', read_only=True
    )

    class Meta:
        model = RecipeIngredient
        fields = ('id', 'name', 'measurement_unit', 'amount')


class RecipeListDetailSerializer(serializers.ModelSerializer):
    is_favorited = serializers.BooleanField(read_only=True)
    is_in_shopping_cart = serializers.BooleanField(read_only=True)
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


class Base64ImageField(serializers.ImageField):
    def to_internal_value(self, data):
        if isinstance(data, str) and data.startswith('data:image'):
            format, imgstr = data.split(';base64,')
            ext = format.split('/')[-1]
            data = ContentFile(base64.b64decode(imgstr), name='temp.' + ext)

        return super().to_internal_value(data)


class IngredientInRecipeCreateSerializer(serializers.ModelSerializer):
    id = serializers.PrimaryKeyRelatedField(
        queryset=Ingredient.objects.all()
    )
    amount = serializers.IntegerField(min_value=1)

    class Meta:
        model = RecipeIngredient
        fields = ('id', 'amount')


class RecipeCreateUpdateSerializer(serializers.ModelSerializer):
    ingredients = IngredientInRecipeCreateSerializer(
        many=True, write_only=True
    )
    tags = serializers.PrimaryKeyRelatedField(
        many=True,
        queryset=Tag.objects.all()
    )
    image = Base64ImageField()
    author = UserSerializer(
        read_only=True,
        default=serializers.CurrentUserDefault()
    )
    is_favorited = serializers.BooleanField(read_only=True, default=False)
    is_in_shopping_cart = serializers.BooleanField(
        read_only=True,
        default=False
    )
    cooking_time = serializers.IntegerField(min_value=1)

    class Meta:
        model = Recipe
        fields = (
            'id', 'tags', 'author', 'ingredients',
            'is_favorited', 'is_in_shopping_cart',
            'name', 'image', 'text', 'cooking_time'
        )

        validators = [
            UniqueTogetherValidator(
                queryset=Recipe.objects.all(),
                fields=('author', 'name')
            )
        ]

    def validate_ingredients(self, ingredients):
        if not ingredients:
            raise serializers.ValidationError(
                'Добавьте хотя бы один ингредиент.'
            )

        ingredients_set = set([ingredient['id'] for ingredient in ingredients])
        if len(ingredients) != len(ingredients_set):
            raise serializers.ValidationError(
                'В списке присутствуют одинаковые ингредиенты.'
            )

        return ingredients

    def validate_tags(self, tags):
        if not tags:
            raise serializers.ValidationError('Добавьте хотя бы один тег.')

        tags_set = set(tags)
        if len(tags) != len(tags_set):
            raise serializers.ValidationError(
                'В списке присутствуют одинаковые теги.'
            )

        return tags

    @staticmethod
    def create_or_update(instance, ingredients, tags):
        RecipeIngredient.objects.bulk_create(
            RecipeIngredient(
                recipe=instance,
                ingredient=ingredient['id'],
                amount=ingredient['amount']
            )
            for ingredient in ingredients
        )
        instance.tags.set(tags)

    def create(self, validated_data):
        ingredients = validated_data.pop('ingredients')
        tags = validated_data.pop('tags')
        recipe = Recipe.objects.create(**validated_data)
        self.create_or_update(recipe, ingredients, tags)
        return recipe

    def update(self, instance, validated_data):
        ingredients = validated_data.pop('ingredients', None)
        tags = validated_data.pop('tags', None)
        self.validate_ingredients(ingredients)
        self.validate_tags(tags)
        instance.ingredients.clear()
        self.create_or_update(instance, ingredients, tags)
        return super().update(instance, validated_data)

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation['ingredients'] = RecipeIngredientSerializer(
            RecipeIngredient.objects.filter(recipe=instance).all(),
            many=True
        ).data
        representation['tags'] = TagSerializer(
            instance.tags.all(),
            many=True
        ).data
        return representation


class RecipeMiniSerializer(serializers.ModelSerializer):
    """Сериализатор для отображения рецептов в списке подписок пользователя."""

    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time')


class FollowSerializer(serializers.ModelSerializer):
    email = serializers.ReadOnlyField(source='following.email')
    id = serializers.ReadOnlyField(source='following.id')
    username = serializers.ReadOnlyField(source='following.username')
    first_name = serializers.ReadOnlyField(source='following.first_name')
    last_name = serializers.ReadOnlyField(source='following.last_name')
    is_subscribed = serializers.SerializerMethodField()
    recipes = serializers.SerializerMethodField()
    recipes_count = serializers.SerializerMethodField()

    class Meta:
        model = Follow
        fields = (
            'email', 'id', 'username', 'first_name',
            'last_name', 'is_subscribed', 'recipes', 'recipes_count'
        )

    def validate(self, data):
        user = self.context.get('request').user
        author = self.context.get('author')

        if user.following.filter(following=author).exists():
            raise serializers.ValidationError(
                detail='Вы уже подписаны на этого автора.',
                code=status.HTTP_400_BAD_REQUEST
            )

        if user == author:
            raise serializers.ValidationError(
                detail='Вы не можете подписаться на самого себя.',
                code=status.HTTP_400_BAD_REQUEST
            )

        return data

    def get_is_subscribed(self, obj):
        user = self.context['request'].user
        following_user = obj.following
        return Follow.objects.filter(
            user=user, following=following_user
        ).exists()

    def get_recipes(self, obj):
        request = self.context.get('request')
        recipes_limit = request.GET.get('recipes_limit', None)
        recipes = Recipe.objects.filter(author=obj.following)
        if recipes_limit is not None and recipes_limit.isdigit():
            recipes = recipes[:int(recipes_limit)]
        return RecipeMiniSerializer(recipes, many=True).data

    def get_recipes_count(self, obj):
        return obj.following.recipes.count()


class BaseFavoriteShoppingListSerializer(serializers.ModelSerializer):
    id = serializers.ReadOnlyField(source='recipe.id')
    name = serializers.ReadOnlyField(source='recipe.name')
    image = serializers.ImageField(source='recipe.image', read_only=True)
    cooking_time = serializers.ReadOnlyField(source='recipe.cooking_time')

    class Meta:
        fields = ('id', 'name', 'image', 'cooking_time')

    def validate(self, data):
        model = self.Meta.model
        user = self.context.get('user')
        recipe_id = self.context.get('recipe_id')

        if not Recipe.objects.filter(id=recipe_id).exists():
            raise serializers.ValidationError(
                detail='Такого рецепта не существует.',
                code=status.HTTP_400_BAD_REQUEST
            )

        recipe = Recipe.objects.get(id=recipe_id)

        if model.objects.filter(user=user, recipe=recipe).exists():
            raise serializers.ValidationError(
                detail='Вы уже добавили этот рецепт.',
                code=status.HTTP_400_BAD_REQUEST
            )

        return data


class FavoriteSerializer(BaseFavoriteShoppingListSerializer):

    class Meta(BaseFavoriteShoppingListSerializer.Meta):
        model = Favorite


class ShoppingListSerializer(BaseFavoriteShoppingListSerializer):

    class Meta(BaseFavoriteShoppingListSerializer.Meta):
        model = ShoppingList
