# Generated by Django 3.2.8 on 2021-10-20 13:28

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('beatmap_collections', '0005_auto_20211020_2022'),
    ]

    operations = [
        migrations.AlterField(
            model_name='collection',
            name='description',
            field=models.CharField(blank=True, max_length=250),
        ),
    ]