# Generated by Django 2.2.6 on 2019-10-24 19:42

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0034_match_date'),
    ]

    operations = [
        migrations.AlterField(
            model_name='streamvod',
            name='film_format',
            field=models.CharField(choices=[('O', 'Original'), ('W', 'World Cup 2017'), ('A', 'APEX'), ('1', 'Korean Contenders season 1'), ('K', 'Korean Contenders season 2'), ('2', 'Overwatch league season 2')], default='O', max_length=1),
        ),
    ]