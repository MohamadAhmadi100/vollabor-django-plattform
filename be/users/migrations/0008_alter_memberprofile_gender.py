# Generated by Django 3.2.4 on 2021-11-24 19:15

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0007_alter_memberprofile_gender'),
    ]

    operations = [
        migrations.AlterField(
            model_name='memberprofile',
            name='gender',
            field=models.CharField(choices=[('Male', 'Male'), ('Female', 'Female')], max_length=6, null=True, verbose_name='Gender'),
        ),
    ]