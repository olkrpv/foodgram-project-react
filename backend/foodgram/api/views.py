from django.db.models import Sum
from django.http import HttpResponse
from django.shortcuts import get_object_or_404

from django_filters.rest_framework import DjangoFilterBackend
from djoser.views import UserViewSet
from rest_framework import filters, status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import SAFE_METHODS, AllowAny, IsAuthenticated
from rest_framework.response import Response

from recipes.models import (
    Favorite,
    Follow,
    Ingredient,
    Recipe,
    ShoppingList,
    Tag,
    User
)

from .filters import RecipeFilter
from .permissions import IsOwnerOrReadOnly
from .serializers import (
    FollowSerializer,
    IngredientSerializer,
    RecipeCreateUpdateSerializer,
    RecipeListDetailSerializer,
    RecipeMiniSerializer,
    TagSerializer
)


class CustomUserViewSet(UserViewSet):

    @action(
        methods=["get"],
        detail=False,
        permission_classes=(IsAuthenticated,)
    )
    def me(self, request, *args, **kwargs):
        self.get_object = self.get_instance
        return self.retrieve(request, *args, **kwargs)

    @action(
        detail=False,
        permission_classes=(IsAuthenticated,)
    )
    def subscriptions(self, request):
        user = self.request.user
        following = Follow.objects.filter(user=user)
        pages = self.paginate_queryset(following)
        serializer = FollowSerializer(
            pages,
            many=True,
            context={'request': request}
        )
        return self.get_paginated_response(serializer.data)

    @action(
        methods=['post', 'delete'],
        detail=True,
        permission_classes=(IsAuthenticated,)
    )
    def subscribe(self, request, *args, **kwargs):
        user = self.request.user
        author = get_object_or_404(User, id=self.kwargs.get('id'))
        is_subscribed = Follow.objects.filter(
            user=user, following=author
        ).exists()

        if request.method == 'POST':
            if is_subscribed:
                return Response(
                    {'errors': 'Вы уже подписаны на этого автора.'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            if user == author:
                return Response(
                    {'errors': 'Вы не можете подписаться на самого себя.'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            Follow.objects.create(user=user, following=author)
            subscription = Follow.objects.get(user=user, following=author)
            serializer = FollowSerializer(
                subscription,
                context={'request': request}
            )
            return Response(
                serializer.data,
                status=status.HTTP_201_CREATED
            )

        if is_subscribed:
            Follow.objects.get(user=user, following=author).delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response(
            {'errors': 'Вы не подписаны на этого пользователя'},
            status=status.HTTP_400_BAD_REQUEST
        )


class TagViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Tag.objects.all()
    permission_classes = (AllowAny,)
    serializer_class = TagSerializer
    pagination_class = None


class IngredientViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Ingredient.objects.all()
    permission_classes = (AllowAny,)
    serializer_class = IngredientSerializer
    filter_backends = (filters.SearchFilter,)
    search_fields = ('^name',)
    pagination_class = None


class RecipeViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.all()
    permission_classes = (IsOwnerOrReadOnly,)
    filter_backends = (DjangoFilterBackend,)
    filterset_class = RecipeFilter

    def get_serializer_class(self):
        if self.request.method in SAFE_METHODS:
            return RecipeListDetailSerializer
        return RecipeCreateUpdateSerializer

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    @action(
        methods=['post', 'delete'],
        detail=True,
        permission_classes=(IsAuthenticated,)
    )
    def favorite(self, request, *args, **kwargs):
        user = self.request.user
        recipe_id = self.kwargs.get('pk')

        if request.method == 'POST':
            if not Recipe.objects.filter(id=recipe_id).exists():
                return Response(
                    {'errors': 'Такого рецепта не существует'},
                    status=status.HTTP_400_BAD_REQUEST
                )

            recipe = Recipe.objects.get(id=recipe_id)
            if Favorite.objects.filter(user=user, recipe=recipe).exists():
                return Response(
                    {'errors': 'Вы уже добавили этот рецепт в избранное.'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            Favorite.objects.create(user=user, recipe=recipe)
            serializer = RecipeMiniSerializer(recipe)
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        recipe = get_object_or_404(Recipe, id=recipe_id)
        if Favorite.objects.filter(user=user, recipe=recipe).exists():
            Favorite.objects.get(user=user, recipe=recipe).delete()
            return Response(
                status=status.HTTP_204_NO_CONTENT
            )
        return Response(
            {'errors': 'Этого рецепта нет в избранном.'},
            status=status.HTTP_400_BAD_REQUEST
        )

    @action(
        methods=['post', 'delete'],
        detail=True,
        permission_classes=(IsAuthenticated,)
    )
    def shopping_cart(self, request, *args, **kwargs):
        user = self.request.user
        recipe_id = self.kwargs.get('pk')

        if request.method == 'POST':
            if not Recipe.objects.filter(id=recipe_id).exists():
                return Response(
                    {'errors': 'Такого рецепта не существует'},
                    status=status.HTTP_400_BAD_REQUEST
                )

            recipe = Recipe.objects.get(id=recipe_id)
            if ShoppingList.objects.filter(user=user, recipe=recipe).exists():
                return Response(
                    {
                        'errors':
                            'Вы уже добавили этот рецепт в список покупок.'
                    },
                    status=status.HTTP_400_BAD_REQUEST
                )
            ShoppingList.objects.create(user=user, recipe=recipe)
            serializer = RecipeMiniSerializer(recipe)
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        recipe = get_object_or_404(Recipe, id=recipe_id)
        if ShoppingList.objects.filter(user=user, recipe=recipe).exists():
            ShoppingList.objects.get(user=user, recipe=recipe).delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response(
            {'errors': 'Этого рецепта нет в списке покупок.'},
            status=status.HTTP_400_BAD_REQUEST
        )

    @action(
        methods=['get'],
        detail=False,
        permission_classes=(IsAuthenticated,)
    )
    def download_shopping_cart(self, request):
        user = self.request.user
        recipes = Recipe.objects.filter(shoppinglist__user=user)
        if not recipes.exists():
            return Response(
                {'errors': 'Список покупок пуст.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        ingredients = Ingredient.objects.filter(
            recipeingredient__recipe__in=recipes
        )
        total_ingredients = ingredients.annotate(
            total=Sum('recipeingredient__amount')
        ).values('name', 'measurement_unit', 'total')

        file_data = 'Список покупок:\n\n'
        for item in total_ingredients:
            file_data += (
                f'- {item["name"]} '
                f'({item["measurement_unit"]}) - {item["total"]}\n'
            )

        filename = 'shopping_cart.txt'
        response = HttpResponse(file_data, content_type='text/plain')
        response['Content-Disposition'] = f'attachment; filename={filename}'
        return response
