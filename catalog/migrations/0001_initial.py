# Generated by Django 5.0.3 on 2024-03-26 09:38

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Movie',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title_text', models.CharField(max_length=1024)),
                ('original_title_text', models.CharField(max_length=1024, null=True)),
                ('year_integer', models.IntegerField()),
                ('poster_text', models.TextField()),
                ('imdb_id_text', models.CharField(max_length=64)),
                ('rating_integer', models.IntegerField()),
            ],
        ),
        migrations.CreateModel(
            name='Genre',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('genre_text', models.CharField(max_length=1024)),
                ('movie', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='catalog.movie')),
            ],
        ),
        migrations.CreateModel(
            name='File',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('file_name_text', models.CharField(max_length=2048)),
                ('type_text', models.CharField(max_length=1024)),
                ('tag_text', models.CharField(max_length=1024)),
                ('hash_text', models.CharField(max_length=512)),
                ('movie', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='catalog.movie')),
            ],
        ),
        migrations.CreateModel(
            name='Director',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name_text', models.CharField(max_length=1024)),
                ('movie', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='catalog.movie')),
            ],
        ),
        migrations.CreateModel(
            name='Country',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('country_text', models.CharField(max_length=1024)),
                ('movie', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='catalog.movie')),
            ],
        ),
        migrations.CreateModel(
            name='Actor',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name_text', models.CharField(max_length=1024)),
                ('movie', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='catalog.movie')),
            ],
        ),
        migrations.CreateModel(
            name='Saga',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name_text', models.CharField(max_length=1024)),
                ('movie', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='catalog.movie')),
            ],
        ),
        migrations.CreateModel(
            name='Screenwriter',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name_text', models.CharField(max_length=1024)),
                ('movie', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='catalog.movie')),
            ],
        ),
    ]