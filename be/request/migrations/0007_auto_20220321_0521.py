# Generated by Django 3.2.4 on 2022-03-21 12:21

import datetime
from django.db import migrations, models
from django.utils.timezone import utc


class Migration(migrations.Migration):

    dependencies = [
        ('request', '0006_auto_20220321_0516'),
    ]

    operations = [
        migrations.AlterField(
            model_name='supervisorreview',
            name='deadlien',
            field=models.DateTimeField(default=datetime.datetime(2022, 3, 21, 12, 21, 17, 800629, tzinfo=utc), null=True),
        ),
        migrations.AlterField(
            model_name='workshopreview',
            name='deadlien',
            field=models.DateTimeField(default=datetime.datetime(2022, 3, 21, 12, 21, 17, 804627, tzinfo=utc), null=True),
        ),
    ]
