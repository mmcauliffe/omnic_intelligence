# Generated by Django 2.0 on 2018-01-11 06:48

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('annotator', '0031_auto_20180111_0148'),
    ]

    operations = [
        migrations.AlterField(
            model_name='match',
            name='spectator_mode',
            field=models.CharField(choices=[('C', 'Color'), ('A', 'Ability'), ('O', 'Original')], default='C', max_length=1),
        ),
    ]
