# Generated by Django 3.2.9 on 2021-11-19 20:11

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('beatmap_collections', '0036_auto_20211116_1700'),
    ]

    operations = [
        migrations.AlterField(
            model_name='beatmapentry',
            name='comment',
            field=models.CharField(blank=True, max_length=250, null=True),
        ),
    ]
