# Generated by Django 2.0 on 2019-02-17 23:24

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0010_auto_20190128_1114'),
    ]

    operations = [
        migrations.AlterField(
            model_name='streamvod',
            name='type',
            field=models.CharField(choices=[('N', 'Not analyzed'), ('G', 'Automatically annotated for in-game/out-of-game'), ('A', 'Rounds automatically annotated'), ('T', 'Game boundaries manually checked'), ('M', 'Round events manually corrected')], default='M', max_length=1),
        ),
    ]
