# Generated by Django 2.0 on 2019-01-22 20:10

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0004_auto_20190122_1449'),
    ]

    operations = [
        migrations.AddField(
            model_name='streamvod',
            name='last_modified',
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='streamvod',
            name='status',
            field=models.CharField(choices=[('A', 'Automatically annotated'), ('T', 'To be annotated'), ('M', 'Manually corrected')], default='A', max_length=1),
        ),
        migrations.AddField(
            model_name='streamvod',
            name='type',
            field=models.CharField(choices=[('A', 'Automatically annotated'), ('T', 'To be annotated'), ('M', 'Manually corrected')], default='G', max_length=1),
        ),
    ]
