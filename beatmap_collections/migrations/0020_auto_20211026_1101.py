# Generated by Django 3.2.8 on 2021-10-26 04:01

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('beatmap_collections', '0019_merge_0017_delete_profile_0018_auto_20211025_2204'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='beatmapentry',
            name='create_date',
        ),
        migrations.AddField(
            model_name='beatmap',
            name='approved_date',
            field=models.DateTimeField(auto_now_add=True, default=django.utils.timezone.now),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='beatmap',
            name='last_update',
            field=models.DateTimeField(auto_now_add=True, default=django.utils.timezone.now),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='beatmap',
            name='submit_date',
            field=models.DateTimeField(auto_now_add=True, default=django.utils.timezone.now),
            preserve_default=False,
        ),
    ]