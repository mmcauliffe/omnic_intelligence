# Generated by Django 2.0 on 2019-01-25 05:59

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0008_remove_event_channel'),
    ]

    operations = [
        migrations.AddField(
            model_name='streamchannel',
            name='youtube_channel_id',
            field=models.CharField(blank=True, max_length=128, null=True),
        ),
    ]
