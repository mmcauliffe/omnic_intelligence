# Generated by Django 2.2.6 on 2019-11-01 23:25

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0036_auto_20191101_1520'),
    ]

    operations = [
        migrations.AddField(
            model_name='teamparticipation',
            name='use_home_color',
            field=models.BooleanField(default=False),
        ),
    ]
