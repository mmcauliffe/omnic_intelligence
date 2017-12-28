# Generated by Django 2.0 on 2017-12-26 00:28

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('annotator', '0017_auto_20171218_0811'),
    ]

    operations = [
        migrations.CreateModel(
            name='ReplayEnd',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('time_point', models.IntegerField()),
                ('round', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='annotator.Round')),
            ],
        ),
        migrations.CreateModel(
            name='ReplayStart',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('time_point', models.IntegerField()),
                ('round', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='annotator.Round')),
            ],
        ),
        migrations.AlterUniqueTogether(
            name='replaystart',
            unique_together={('round', 'time_point')},
        ),
        migrations.AlterUniqueTogether(
            name='replayend',
            unique_together={('round', 'time_point')},
        ),
    ]
