# Generated by Django 3.2.4 on 2022-03-30 23:51

import datetime
from django.db import migrations, models
from django.utils.timezone import utc


class Migration(migrations.Migration):

    dependencies = [
        ('request', '0015_auto_20220330_1631'),
    ]

    operations = [
        migrations.AlterField(
            model_name='badgerequest',
            name='other',
            field=models.BooleanField(default=False, null=True),
        ),
        migrations.AlterField(
            model_name='badgerequest',
            name='status',
            field=models.CharField(choices=[('New', 'New'), ('Reject-badge', 'Reject-badge'), ('Review', 'Review'), ('Set-session', 'Set-session'), ('Approve-decline', 'Approve-decline'), ('Interview', 'Interview'), ('Expert-view', 'Expert-view'), ('send_manager', 'Send to manager'), ('decline-review-interview', 'Decline review, interview'), ('Accept', 'Accept'), ('Reject', 'Reject')], default='New', max_length=100),
        ),
        migrations.AlterField(
            model_name='supervisorreview',
            name='deadlien',
            field=models.DateTimeField(default=datetime.datetime(2022, 3, 30, 23, 51, 15, 429602, tzinfo=utc), null=True),
        ),
        migrations.AlterField(
            model_name='workshopreview',
            name='deadlien',
            field=models.DateTimeField(default=datetime.datetime(2022, 3, 30, 23, 51, 15, 429602, tzinfo=utc), null=True),
        ),
    ]
