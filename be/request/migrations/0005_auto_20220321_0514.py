# Generated by Django 3.2.4 on 2022-03-21 12:14

import datetime
from django.db import migrations, models
from django.utils.timezone import utc


class Migration(migrations.Migration):

    dependencies = [
        ('request', '0004_auto_20220321_0225'),
    ]

    operations = [
        migrations.AlterField(
            model_name='supervisorreview',
            name='deadlien',
            field=models.DateTimeField(default=datetime.datetime(2022, 3, 21, 12, 14, 30, 837060, tzinfo=utc), null=True),
        ),
        migrations.AlterField(
            model_name='workshopreview',
            name='deadlien',
            field=models.DateTimeField(default=datetime.datetime(2022, 3, 21, 12, 14, 30, 841058, tzinfo=utc), null=True),
        ),
    ]