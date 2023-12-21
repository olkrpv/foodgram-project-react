# Generated by Django 3.2.16 on 2023-12-21 07:07

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('recipes', '0014_alter_recipe_image'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='tag',
            name='color_hex',
        ),
        migrations.AddField(
            model_name='tag',
            name='color',
            field=models.CharField(max_length=7, null=True, unique=True, verbose_name='Цветовой код'),
        ),
        migrations.AlterField(
            model_name='tag',
            name='slug',
            field=models.SlugField(max_length=200, null=True, unique=True, verbose_name='Слаг'),
        ),
    ]
