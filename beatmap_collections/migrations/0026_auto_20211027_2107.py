# Generated by Django 3.2.8 on 2021-10-27 21:07

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('beatmap_collections', '0025_auto_20211027_2047'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='beatmapentry',
            name='description',
        ),
        migrations.RemoveField(
            model_name='beatmapentry',
            name='user',
        ),
    ]
