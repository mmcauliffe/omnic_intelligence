# Generated by Django 2.2.3 on 2019-10-06 00:01

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0033_auto_20191003_1629'),
    ]

    operations = [
        migrations.AddField(
            model_name='match',
            name='date',
            field=models.DateField(blank=True, null=True),
        ),
    ]
