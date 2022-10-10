# Generated by Django 3.2.4 on 2022-04-13 02:20

import datetime
from django.db import migrations, models
from django.utils.timezone import utc


class Migration(migrations.Migration):

    dependencies = [
        ('request', '0024_auto_20220410_0843'),
    ]

    operations = [
        migrations.AddField(
            model_name='workshoprequest',
            name='rejected_date',
            field=models.DateField(null=True),
        ),
        migrations.AlterField(
            model_name='supervisorrequest',
            name='status',
            field=models.CharField(choices=[('New', 'New'), ('Review', 'Review'), ('reviewer_evaluated', 'evaluated Reviewer'), ('reviewer_accept', 'Accept Reviewer '), ('reviewer_reject', 'Reject Reviewer '), ('send_to_manager', 'Send to manager'), ('revise_by_manager', 'Revise by manager'), ('revise_by_expert', 'Revise by expert'), ('accepted_by_manager', 'Accepted by manager'), ('accepted_by_expert', 'Accepted by expert'), ('rejected_by_manager', 'Rejected by manager'), ('rejected_by_expert', 'Rejected by expert')], default='New', max_length=100),
        ),
        migrations.AlterField(
            model_name='supervisorreview',
            name='deadlien',
            field=models.DateTimeField(default=datetime.datetime(2022, 4, 13, 2, 19, 22, 46025, tzinfo=utc), null=True),
        ),
        migrations.AlterField(
            model_name='supervisorreview',
            name='status',
            field=models.CharField(choices=[('new', 'New'), ('reject', 'Reject'), ('accept', 'Accept'), ('evaluated', 'Evaluated'), ('revise', 'Revise'), ('done', 'Done'), ('not_see', 'Not see'), ('breach_of_promis', 'Breach or promis')], default='new', max_length=20, null=True),
        ),
        migrations.AlterField(
            model_name='workshoprequest',
            name='status',
            field=models.CharField(choices=[('New', 'New'), ('Review', 'Review'), ('reviewer_evaluated', 'evaluated Reviewer'), ('reviewer_reject', 'Reject Reviewer '), ('reviewer_accept', 'Accept Reviewer '), ('send_to_manager', 'Send to manager'), ('accepted_by_manager', 'Accepted by manager'), ('accepted_by_expert', 'Accepted by manager'), ('rejected_by_manager', 'Rejected by manager'), ('rejected_by_expert', 'Rejected by manager'), ('revised_by_manager', 'Revised by manager'), ('revised_by_expert', 'Revised by manager')], default='New', max_length=100),
        ),
        migrations.AlterField(
            model_name='workshopreview',
            name='deadlien',
            field=models.DateTimeField(default=datetime.datetime(2022, 4, 13, 2, 19, 22, 51022, tzinfo=utc), null=True),
        ),
    ]