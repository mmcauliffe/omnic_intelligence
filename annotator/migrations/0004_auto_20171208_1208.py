# Generated by Django 2.0 on 2017-12-08 17:08

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('annotator', '0003_remove_map_is_koth'),
    ]

    operations = [
        migrations.AddField(
            model_name='ability',
            name='name',
            field=models.CharField(default='', max_length=128),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='match',
            name='teams',
            field=models.ManyToManyField(to='annotator.Team'),
        ),
        migrations.AddField(
            model_name='npc',
            name='name',
            field=models.CharField(default='', max_length=128),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='participation',
            name='players',
            field=models.ManyToManyField(to='annotator.Player'),
        ),
    ]
