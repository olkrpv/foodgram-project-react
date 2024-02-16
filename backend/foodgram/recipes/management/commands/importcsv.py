import csv

from django.core.management.base import BaseCommand

from recipes.models import Ingredient


class Command(BaseCommand):
    help = 'Загружает ингредиенты из файла data/ingredients.csv'

    def add_arguments(self, parser):
        parser.add_argument(
            'filename',
            type=str,
            help='Путь до файла с ингредиентами'
        )

    def handle(self, *args, **options):
        filename = options['filename']
        with open(filename) as f:
            reader = csv.reader(f)
            created_count = 0
            for row in reader:
                name, unit = row
                ingredient, created = Ingredient.objects.get_or_create(
                    name=name, measurement_unit=unit
                )
                if created:
                    created_count += 1

            self.stdout.write(
                self.style.SUCCESS(
                    f'Добавлено {created_count} ингредиентов'
                )
            )
