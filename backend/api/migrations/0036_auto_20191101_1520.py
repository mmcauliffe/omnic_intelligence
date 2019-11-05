# Generated by Django 2.2.6 on 2019-11-01 21:20

import colorful.fields
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0035_auto_20191024_1342'),
    ]

    operations = [
        migrations.AddField(
            model_name='team',
            name='away_color',
            field=colorful.fields.RGBColorField(default='#ff122c'),
        ),
        migrations.AddField(
            model_name='team',
            name='home_color',
            field=colorful.fields.RGBColorField(default='#54fefd'),
        ),
    ]