# Generated by Django 3.2.4 on 2021-09-16 14:09

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('task_tracker', '0002_percent'),
    ]

    operations = [
        migrations.DeleteModel(
            name='Percent',
        ),
        migrations.AddField(
            model_name='tasktracker',
            name='task_percent',
            field=models.IntegerField(default=0),
        ),
    ]