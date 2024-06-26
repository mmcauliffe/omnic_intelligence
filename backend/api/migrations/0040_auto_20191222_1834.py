# Generated by Django 2.2.6 on 2019-12-23 01:34

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0039_auto_20191109_1144'),
    ]

    operations = [
        migrations.AlterField(
            model_name='streamvod',
            name='film_format',
            field=models.CharField(choices=[('O', 'Original'), ('W', 'World Cup 2017'), ('A', 'APEX'), ('1', 'Korean Contenders season 1'), ('K', 'Korean Contenders season 2'), ('U', 'Australia Contenders season 2'), ('G', 'Gauntlet 2019'), ('2', 'Overwatch league season 2')], default='O', max_length=1),
        ),
        migrations.CreateModel(
            name='Submap',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=128, unique=True)),
                ('map', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='api.Map')),
            ],
        ),
        migrations.AddField(
            model_name='round',
            name='submap',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='api.Submap'),
        ),
    ]
