# Generated by Django 3.2.8 on 2021-10-27 20:25

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('beatmap_collections', '0022_alter_beatmap_tags'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='beatmap',
            name='collection',
        ),
    ]