# Generated by Django 3.0.5 on 2020-04-13 16:40

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('macau_game', '0004_game_special_state'),
    ]

    operations = [
        migrations.AddField(
            model_name='game',
            name='demand_time',
            field=models.SmallIntegerField(default=0),
        ),
    ]