from django.contrib.auth import get_user_model
from django.db import models

from colorfield.fields import ColorField

FIELD_MAX_LENGTH = 200

User = get_user_model()


class Ingredient(models.Model):
    name = models.CharField(
        max_length=FIELD_MAX_LENGTH,
        verbose_name='Название',
        db_index=True
    )
    measurement_unit = models.CharField(
        max_length=FIELD_MAX_LENGTH,
        verbose_name='Единица измерения'
    )

    class Meta:
        verbose_name = 'Ингредиент'
        verbose_name_plural = 'Ингредиенты'

    def __str__(self):
        return self.name


class Tag(models.Model):
    name = models.CharField(
        max_length=FIELD_MAX_LENGTH,
        verbose_name='Название',
        unique=True
    )
    color = ColorField()
    slug = models.SlugField(
        max_length=FIELD_MAX_LENGTH,
        null=True,
        verbose_name='Уникальный слаг',
        unique=True
    )

    class Meta:
        verbose_name = 'Тег'
        verbose_name_plural = 'Теги'

    def __str__(self):
        return self.name


class RecipeQuerySet(models.QuerySet):
    def with_favorite_shopping_info(self, user):
        if user.is_authenticated:
            return self.annotate(
                is_favorited=models.Exists(
                    Favorite.objects.filter(
                        user=user, recipe=models.OuterRef('id')
                    )
                ),
                is_in_shopping_cart=models.Exists(
                    ShoppingList.objects.filter(
                        user=user, recipe=models.OuterRef('id')
                    )
                )
            )

        return self.annotate(
            is_favorited=models.Value(False),
            is_in_shopping_cart=models.Value(False)
        )


class RecipeManager(models.Manager):
    def get_queryset(self):
        return RecipeQuerySet(self.model, using=self._db)

    def with_favorite_shopping_info(self, user):
        return self.get_queryset().with_favorite_shopping_info(user)


class Recipe(models.Model):
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='recipes',
        verbose_name='Автор',
        db_index=True
    )
    name = models.CharField(
        max_length=FIELD_MAX_LENGTH,
        verbose_name='Название',
        db_index=True
    )
    image = models.ImageField(
        upload_to='recipes_images',
        verbose_name='Фото'
    )
    text = models.TextField(verbose_name='Описание')
    cooking_time = models.PositiveIntegerField(
        verbose_name='Время приготовления (в минутах)'
    )
    ingredients = models.ManyToManyField(
        Ingredient,
        through='RecipeIngredient',
        related_name='recipes',
        verbose_name='Ингредиенты'
    )
    tags = models.ManyToManyField(
        Tag,
        related_name='recipes',
        verbose_name='Теги',
        db_index=True
    )
    pub_date = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Дата публикации',
        db_index=True
    )

    objects = RecipeManager()

    def favorite_users_count(self):
        return self.favorites.count()

    favorite_users_count.short_description = 'Число добавлений в избранное'

    class Meta:
        ordering = ('-pub_date',)
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'

        constraints = [
            models.UniqueConstraint(
                fields=['author', 'name'],
                name='unique_recipe_from_author'
            )
        ]

    def __str__(self):
        return self.name


class RecipeIngredient(models.Model):
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        verbose_name='Рецепт'
    )
    ingredient = models.ForeignKey(
        Ingredient,
        on_delete=models.CASCADE,
        verbose_name='Ингредиент'
    )
    amount = models.PositiveIntegerField(verbose_name='Количество')

    class Meta:
        verbose_name = 'Ингредиент в рецепте'
        verbose_name_plural = 'Ингредиенты в рецептах'

    def __str__(self):
        return f'{self.ingredient} в рецепте {self.recipe}'


class Follow(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='following',
        verbose_name='Подписчик'
    )
    following = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='followers',
        verbose_name='Преследуемый'
    )

    class Meta:
        verbose_name = 'Подписка'
        verbose_name_plural = 'Подписки'

        constraints = [
            models.UniqueConstraint(
                fields=['user', 'following'],
                name='unique_user_following'
            )
        ]

    def __str__(self):
        return f'{self.user} подписан на {self.following}'


class Favorite(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='favorites',
        verbose_name='Добавивший в избранное'
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='favorites',
        verbose_name='Избранный рецепт'
    )

    class Meta:
        verbose_name = 'Избранное'
        verbose_name_plural = 'Избранное'

        constraints = [
            models.UniqueConstraint(
                fields=['user', 'recipe'],
                name='unique_favorite_recipe'
            )
        ]

    def __str__(self):
        return f'{self.user} добавил в избранное {self.recipe}'


class ShoppingList(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='shoppinglist',
        verbose_name='Добавивший в список покупок'
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='shoppinglist',
        verbose_name='Добавленный в список покупок'
    )

    class Meta:
        verbose_name = 'Список покупок'
        verbose_name_plural = 'Список покупок'

        constraints = [
            models.UniqueConstraint(
                fields=['user', 'recipe'],
                name='unique_recipe_in_shopping_list'
            )
        ]

    def __str__(self):
        return f'{self.user} добавил в список покупок {self.recipe}'
