from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()


class Ingredient(models.Model):
    name = models.CharField(max_length=200)
    measurement_unit = models.CharField(max_length=200)


class Tag(models.Model):
    name = models.CharField(max_length=200)
    color_hex = models.CharField(max_length=7)
    slug = models.SlugField(max_length=64, unique=True)


class Recipe(models.Model):
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='recipes'
    )
    name = models.CharField(max_length=200)
    # image = models.ImageField()
    text = models.TextField()
    # cooking_time = models.DurationField()
    ingredients = models.ManyToManyField(
        Ingredient,
        through='RecipeIngredient',
        related_name='recipes'
    )
    tags = models.ManyToManyField(
        Tag,
        related_name='recipes'
    )


class RecipeIngredient(models.Model):
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE
    )
    ingredient = models.ForeignKey(
        Ingredient,
        on_delete=models.CASCADE
    )
    amount = models.PositiveIntegerField()


class Favorite(models.Model):
    ...


class Following(models.Model):
    ...


class ShoppingList(models.Model):
    ...
