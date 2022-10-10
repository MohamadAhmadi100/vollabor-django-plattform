# Generated by Django 3.2.4 on 2022-08-14 08:58

import datetime
from django.db import migrations, models
from django.utils.timezone import utc


class Migration(migrations.Migration):

    dependencies = [
        ('research', '0011_auto_20220811_1105'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='requestuserforproject',
            name='expert_obj',
        ),
        migrations.AlterField(
            model_name='industryexpertforsupervisor',
            name='status',
            field=models.CharField(choices=[('u', 'u'), ('a', 'Accept'), ('r', 'Reject'), ('not-pay', 'not-pay'), ('resubmition', 'Resubmition'), ('m', 'Main supervisor'), ('b', 'Returned'), ('v', 'Reviewer'), ('not_response_proposal', 'Not response proposal'), ('not_response_proposal_send_to_director', 'Not response proposal send to the director'), ('reject_proposal_by_expert', 'Reject proposal by director'), ('resubmition-to-director', 'resubmition-to-director'), ('d', 'Director'), ('h', 'Reject proposal by director'), ('t', 'Sned contract to supervisor'), ('director_revise_contract', 'Director revise contract'), ('withdrew', 'withdrew'), ('z', 'Send contract supervisor for director'), ('g', 'expert chek contract'), ('n', 'Create new project'), ('x', 'Send contract to expert by director'), ('reject_contract', 'Reject contract'), ('not_see', 'Not see'), ('revise-proposal-to-expert', 'Revise proposal to the expert'), ('special_expert', 'special expert'), ('special_expert_review', 'special expert review'), ('special_expert_create_project', 'special expert create project'), ('report', 'report expert'), ('report_d', 'report director'), ('deleted', 'deleted')], default='u', max_length=50, null=True),
        ),
        migrations.AlterField(
            model_name='industryformclient',
            name='end_date',
            field=models.DateField(default=datetime.datetime(2022, 8, 14, 8, 58, 19, 800165, tzinfo=utc), null=True, verbose_name='End Date'),
        ),
        migrations.AlterField(
            model_name='industryformclient',
            name='start_date',
            field=models.DateField(default=datetime.datetime(2022, 8, 14, 8, 58, 19, 800165, tzinfo=utc), null=True, verbose_name='Strat Date'),
        ),
        migrations.AlterField(
            model_name='researchmeeting',
            name='date_meeting',
            field=models.DateField(default=datetime.datetime(2022, 8, 14, 8, 58, 19, 806149, tzinfo=utc)),
        ),
        migrations.AlterField(
            model_name='researchmeeting',
            name='time_meeting',
            field=models.TimeField(default=datetime.datetime(2022, 8, 14, 8, 58, 19, 806149, tzinfo=utc)),
        ),
        migrations.AlterField(
            model_name='timeprogramming',
            name='end_date',
            field=models.DateField(default=datetime.datetime(2022, 8, 14, 8, 58, 19, 803157, tzinfo=utc), null=True),
        ),
        migrations.AlterField(
            model_name='timeprogramming',
            name='start_date',
            field=models.DateField(default=datetime.datetime(2022, 8, 14, 8, 58, 19, 803157, tzinfo=utc), null=True),
        ),
    ]
