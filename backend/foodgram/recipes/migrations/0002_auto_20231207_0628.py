# Generated by Django 3.2.16 on 2023-12-07 06:28

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('recipes', '0001_initial'),
    ]

    operations = [
        migrations.DeleteModel(
            name='Favorite',
        ),
        migrations.DeleteModel(
            name='Following',
        ),
        migrations.DeleteModel(
            name='ShoppingList',
        ),
    ]