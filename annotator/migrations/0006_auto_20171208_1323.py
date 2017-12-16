# Generated by Django 2.0 on 2017-12-08 18:23

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('annotator', '0005_auto_20171208_1231'),
    ]

    operations = [
        migrations.CreateModel(
            name='Affiliation',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('start', models.DateField()),
                ('end', models.DateField()),
                ('player', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='annotator.Player')),
                ('team', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='annotator.Team')),
            ],
        ),
        migrations.AlterModelOptions(
            name='ability',
            options={'ordering': ['hero', 'name'], 'verbose_name_plural': 'abilities'},
        ),
        migrations.AlterModelOptions(
            name='match',
            options={'verbose_name_plural': 'matches'},
        ),
        migrations.AlterModelOptions(
            name='npc',
            options={'verbose_name': 'NPC', 'verbose_name_plural': 'NPCs'},
        ),
        migrations.AlterField(
            model_name='match',
            name='event',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='annotator.Event'),
        ),
        migrations.AddField(
            model_name='team',
            name='players',
            field=models.ManyToManyField(through='annotator.Affiliation', to='annotator.Player'),
        ),
    ]
