# Generated by Django 5.2.1 on 2025-05-26 19:20

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('movies', '0002_rename_description_movie_overview'),
    ]

    operations = [
        migrations.AlterField(
            model_name='movie',
            name='title',
            field=models.CharField(max_length=255, unique=True),
        ),
    ]
