# Generated by Django 3.0.2 on 2020-03-03 16:14

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('macau_game', '0003_game_full'),
    ]

    operations = [
        migrations.AddField(
            model_name='game',
            name='special_state',
            field=models.SmallIntegerField(default=0),
        ),
    ]