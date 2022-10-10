# Generated by Django 3.2.4 on 2022-03-19 12:11

import datetime
from django.db import migrations, models
from django.utils.timezone import utc


class Migration(migrations.Migration):

    dependencies = [
        ('request', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='supervisorrequest',
            name='id_request',
            field=models.CharField(max_length=20, null=True),
        ),
        migrations.AddField(
            model_name='workshoprequest',
            name='access_accept_reject',
            field=models.BooleanField(default=False, null=True),
        ),
        migrations.AddField(
            model_name='workshoprequest',
            name='comment',
            field=models.TextField(blank=True, default='', null=True),
        ),
        migrations.AddField(
            model_name='workshoprequest',
            name='id_request',
            field=models.CharField(max_length=20, null=True),
        ),
        migrations.AlterField(
            model_name='badgerequest',
            name='status',
            field=models.CharField(choices=[('New', 'New'), ('Review', 'Review'), ('Set-session', 'Set-session'), ('Approve-decline', 'Approve-decline'), ('Interview', 'Interview'), ('Expert-view', 'Expert-view'), ('send_manager', 'Send to manager'), ('Accept', 'Accept'), ('Reject', 'Reject')], default='New', max_length=100),
        ),
        migrations.AlterField(
            model_name='supervisorreview',
            name='deadlien',
            field=models.DateTimeField(default=datetime.datetime(2022, 3, 19, 12, 11, 50, 225311, tzinfo=utc), null=True),
        ),
        migrations.AlterField(
            model_name='workshopreview',
            name='deadlien',
            field=models.DateTimeField(default=datetime.datetime(2022, 3, 19, 12, 11, 50, 229309, tzinfo=utc), null=True),
        ),
    ]