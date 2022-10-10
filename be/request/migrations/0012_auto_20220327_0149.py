# Generated by Django 3.2.4 on 2022-03-27 08:49

import datetime
from django.db import migrations, models
from django.utils.timezone import utc


class Migration(migrations.Migration):

    dependencies = [
        ('request', '0011_auto_20220326_1224'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='badgerequest',
            name='updated',
        ),
        migrations.AlterField(
            model_name='supervisorreview',
            name='deadlien',
            field=models.DateTimeField(default=datetime.datetime(2022, 3, 27, 8, 49, 40, 833160, tzinfo=utc), null=True),
        ),
        migrations.AlterField(
            model_name='workshopreview',
            name='deadlien',
            field=models.DateTimeField(default=datetime.datetime(2022, 3, 27, 8, 49, 40, 838155, tzinfo=utc), null=True),
        ),
    ]
