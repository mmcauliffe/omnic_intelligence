# Generated by Django 2.2.3 on 2019-09-01 17:50

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0023_auto_20190901_1138'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='ultimate',
            options={'ordering': ['round', 'gained', 'player']},
        ),
        migrations.RenameField(
            model_name='ultimate',
            old_name='ended_at',
            new_name='ended',
        ),
        migrations.RenameField(
            model_name='ultimate',
            old_name='gained_at',
            new_name='gained',
        ),
        migrations.RenameField(
            model_name='ultimate',
            old_name='used_at',
            new_name='used',
        ),
    ]
