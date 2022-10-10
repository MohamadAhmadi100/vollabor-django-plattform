# Generated by Django 3.2.4 on 2022-03-26 19:14

import datetime
from django.db import migrations, models
from django.utils.timezone import utc


class Migration(migrations.Migration):

    dependencies = [
        ('request', '0009_auto_20220326_0513'),
    ]

    operations = [
        migrations.AddField(
            model_name='badgeexpert',
            name='access_accept_reject',
            field=models.BooleanField(default=False, null=True),
        ),
        migrations.AlterField(
            model_name='supervisorreview',
            name='deadlien',
            field=models.DateTimeField(default=datetime.datetime(2022, 3, 26, 19, 14, 35, 369215, tzinfo=utc), null=True),
        ),
        migrations.AlterField(
            model_name='workshopreview',
            name='deadlien',
            field=models.DateTimeField(default=datetime.datetime(2022, 3, 26, 19, 14, 35, 376209, tzinfo=utc), null=True),
        ),
    ]