# Generated by Django 2.0 on 2018-03-14 01:28

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('annotator', '0044_auto_20180313_2049'),
    ]

    operations = [
        migrations.AlterField(
            model_name='streamvod',
            name='title',
            field=models.CharField(max_length=256),
        ),
    ]
