# Generated by Django 2.2.6 on 2019-11-05 02:22

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0037_teamparticipation_use_home_color'),
    ]

    operations = [
        migrations.CreateModel(
            name='Assist',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('order', models.IntegerField()),
                ('kill', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='api.KillFeedEvent')),
                ('player', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='api.Player')),
            ],
            options={
                'ordering': ['order'],
            },
        ),
        migrations.AddField(
            model_name='killfeedevent',
            name='assists',
            field=models.ManyToManyField(through='api.Assist', to='api.Player'),
        ),
    ]