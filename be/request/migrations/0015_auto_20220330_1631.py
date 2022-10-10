# Generated by Django 3.2.4 on 2022-03-30 23:31

import datetime
from django.db import migrations, models
import django.db.models.deletion
from django.utils.timezone import utc


class Migration(migrations.Migration):

    dependencies = [
        ('request', '0014_auto_20220327_0447'),
    ]

    operations = [
        migrations.AddField(
            model_name='badgerequest',
            name='other',
            field=models.BooleanField(null=True),
        ),
        migrations.AddField(
            model_name='supervisorreview',
            name='score_1',
            field=models.IntegerField(default=0, null=True),
        ),
        migrations.AddField(
            model_name='supervisorreview',
            name='score_10',
            field=models.IntegerField(default=0, null=True),
        ),
        migrations.AddField(
            model_name='supervisorreview',
            name='score_2',
            field=models.IntegerField(default=0, null=True),
        ),
        migrations.AddField(
            model_name='supervisorreview',
            name='score_3',
            field=models.IntegerField(default=0, null=True),
        ),
        migrations.AddField(
            model_name='supervisorreview',
            name='score_4',
            field=models.IntegerField(default=0, null=True),
        ),
        migrations.AddField(
            model_name='supervisorreview',
            name='score_5',
            field=models.IntegerField(default=0, null=True),
        ),
        migrations.AddField(
            model_name='supervisorreview',
            name='score_6',
            field=models.IntegerField(default=0, null=True),
        ),
        migrations.AddField(
            model_name='supervisorreview',
            name='score_7',
            field=models.IntegerField(default=0, null=True),
        ),
        migrations.AddField(
            model_name='supervisorreview',
            name='score_8',
            field=models.IntegerField(default=0, null=True),
        ),
        migrations.AddField(
            model_name='supervisorreview',
            name='score_9',
            field=models.IntegerField(default=0, null=True),
        ),
        migrations.AddField(
            model_name='workshopreview',
            name='score_1',
            field=models.IntegerField(default=0, null=True),
        ),
        migrations.AddField(
            model_name='workshopreview',
            name='score_10',
            field=models.IntegerField(default=0, null=True),
        ),
        migrations.AddField(
            model_name='workshopreview',
            name='score_2',
            field=models.IntegerField(default=0, null=True),
        ),
        migrations.AddField(
            model_name='workshopreview',
            name='score_3',
            field=models.IntegerField(default=0, null=True),
        ),
        migrations.AddField(
            model_name='workshopreview',
            name='score_4',
            field=models.IntegerField(default=0, null=True),
        ),
        migrations.AddField(
            model_name='workshopreview',
            name='score_5',
            field=models.IntegerField(default=0, null=True),
        ),
        migrations.AddField(
            model_name='workshopreview',
            name='score_6',
            field=models.IntegerField(default=0, null=True),
        ),
        migrations.AddField(
            model_name='workshopreview',
            name='score_7',
            field=models.IntegerField(default=0, null=True),
        ),
        migrations.AddField(
            model_name='workshopreview',
            name='score_8',
            field=models.IntegerField(default=0, null=True),
        ),
        migrations.AddField(
            model_name='workshopreview',
            name='score_9',
            field=models.IntegerField(default=0, null=True),
        ),
        migrations.AlterField(
            model_name='supervisorreview',
            name='deadlien',
            field=models.DateTimeField(default=datetime.datetime(2022, 3, 30, 23, 31, 5, 561359, tzinfo=utc), null=True),
        ),
        migrations.AlterField(
            model_name='workshoprequest',
            name='status',
            field=models.CharField(choices=[('New', 'New'), ('Review', 'Review'), ('reviewer_evaluated', 'evaluated Reviewer'), ('reviewer_reject', 'Reject Reviewer '), ('reviewer_accept', 'Accept Reviewer '), ('send_to_manager', 'Send to manager'), ('accepted_by_manager', 'Accepted by manager'), ('rejected_by_manager', 'Rejected by manager')], default='New', max_length=100),
        ),
        migrations.AlterField(
            model_name='workshopreview',
            name='deadlien',
            field=models.DateTimeField(default=datetime.datetime(2022, 3, 30, 23, 31, 5, 561359, tzinfo=utc), null=True),
        ),
        migrations.AlterField(
            model_name='workshopreview',
            name='workshop',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='workshop_request', to='request.workshoprequest'),
        ),
    ]
