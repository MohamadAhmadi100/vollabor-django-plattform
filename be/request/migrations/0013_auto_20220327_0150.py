# Generated by Django 3.2.4 on 2022-03-27 08:50

import datetime
from django.db import migrations, models
from django.utils.timezone import utc


class Migration(migrations.Migration):

    dependencies = [
        ('request', '0012_auto_20220327_0149'),
    ]

    operations = [
        migrations.AddField(
            model_name='badgerequest',
            name='position',
            field=models.CharField(choices=[('Interview', 'Interview'), ('Review', 'Review')], max_length=20, null=True),
        ),
        migrations.AddField(
            model_name='badgerequest',
            name='updated',
            field=models.DateTimeField(auto_now=True),
        ),
        migrations.AlterField(
            model_name='supervisorreview',
            name='deadlien',
            field=models.DateTimeField(default=datetime.datetime(2022, 3, 27, 8, 50, 46, 535712, tzinfo=utc), null=True),
        ),
        migrations.AlterField(
            model_name='workshopreview',
            name='deadlien',
            field=models.DateTimeField(default=datetime.datetime(2022, 3, 27, 8, 50, 46, 542708, tzinfo=utc), null=True),
        ),
    ]
