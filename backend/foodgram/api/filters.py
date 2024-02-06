from django_filters import rest_framework as filters
from django.db.models import Q

from recipes.models import Recipe


class RecipeFilter(filters.FilterSet):
    tags = filters.CharFilter(method='filter_tags')  # field_name='tags__slug')
    is_favorited = filters.BooleanFilter(method='filter_favorited')
    is_in_shopping_cart = filters.BooleanFilter(method='filter_shopping_cart')

    class Meta:
        model = Recipe
        fields = ('author', 'tags')

    def filter_tags(self, queryset, name, value):
        values = self.request.GET.getlist('tags')
        q_objects = Q()
        for tag in values:
            q_objects |= Q(tags__slug=tag)
        return queryset.filter(q_objects)

    def filter_favorited(self, queryset, name, value):
        user = self.request.user
        if user.is_authenticated:
            if value == 1:
                return queryset.filter(favorites__user=user)
            if value == 0:
                return queryset.exclude(favorites__user=user)
        return queryset

    def filter_shopping_cart(self, queryset, name, value):
        user = self.request.user
        if user.is_authenticated:
            if value == 1:
                return queryset.filter(shoppinglist__user=user)
            if value == 0:
                return queryset.exclude(shoppinglist__user=user)
        return queryset
