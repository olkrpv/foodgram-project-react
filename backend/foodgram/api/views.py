from rest_framework import viewsets, filters
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny, IsAuthenticated, SAFE_METHODS
from rest_framework.response import Response
from djoser.views import UserViewSet
from django_filters.rest_framework import DjangoFilterBackend

from recipes.models import Tag, Ingredient, Recipe, Follow, User

from .filters import RecipeFilter
from .serializers import TagSerializer, IngredientSerializer, RecipeListDetailSerializer, RecipeCreateUpdateSerializer, FollowSerializer
from .permissions import IsOwnerOrReadOnly


class CustomUserViewSet(UserViewSet):

    @action(
        methods=["get"],
        detail=False,
        permission_classes=(IsAuthenticated,)
    )
    def me(self, request, *args, **kwargs):
        self.get_object = self.get_instance
        return self.retrieve(request, *args, **kwargs)

    @action(detail=False)
    def subscriptions(self, request):
        user = self.request.user
        following = Follow.objects.filter(user=user).values('following')
        following_users = User.objects.filter(id__in=following)
        pages = self.paginate_queryset(following_users)

        recipes_limit = request.query_params.get('recipes_limit', None)
        serializer_context = {'request': request}
        if recipes_limit is not None:
            serializer_context['recipes_limit'] = int(recipes_limit)

        serializer = FollowSerializer(
            pages,
            many=True,
            context=serializer_context
        )
        return self.get_paginated_response(serializer.data)


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
