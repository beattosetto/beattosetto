# Generated by Django 3.2.9 on 2021-11-19 20:36

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('beatmap_collections', '0038_alter_beatmapentry_comment'),
    ]

    operations = [
        migrations.AlterField(
            model_name='beatmapentry',
            name='comment',
            field=models.CharField(blank=True, max_length=250, null=True),
        ),
    ]