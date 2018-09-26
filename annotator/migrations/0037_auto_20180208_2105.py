# Generated by Django 2.0 on 2018-02-09 02:05

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('annotator', '0036_auto_20180208_2056'),
    ]

    operations = [
        migrations.AlterField(
            model_name='killassist',
            name='kill',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='assists', to='annotator.Kill'),
        ),
        migrations.AlterField(
            model_name='killnpcassist',
            name='kill',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='assists', to='annotator.KillNPC'),
        ),
    ]
