# Generated by Django 2.0 on 2017-12-08 17:03

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('annotator', '0002_auto_20171208_1202'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='map',
            name='is_koth',
        ),
    ]
