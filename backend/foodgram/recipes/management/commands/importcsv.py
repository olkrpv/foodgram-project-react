import csv

from django.core.management.base import BaseCommand

from recipes.models import Ingredient


class Command(BaseCommand):
    help = 'Загружает ингредиенты из файла data/ingredients.csv'

    def handle(self, *args, **options):
        with open('../../data/ingredients.csv') as f:
            reader = csv.reader(f)
            created_count = 0
            for row in reader:
                name, unit = row
                ingredient, created = Ingredient.objects.get_or_create(name=name, measurement_unit=unit)
                if created:
                    created_count += 1

            self.stdout.write(
                self.style.SUCCESS(
                    f'Добавлено {created_count} ингредиентов'
                )
            )

