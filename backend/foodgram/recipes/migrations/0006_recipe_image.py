# Generated by Django 3.2.16 on 2023-12-07 12:44

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('recipes', '0005_alter_shoppinglist_options'),
    ]

    operations = [
        migrations.AddField(
            model_name='recipe',
            name='image',
            field=models.ImageField(blank=True, upload_to='recipes_images', verbose_name='Фото'),
        ),
    ]