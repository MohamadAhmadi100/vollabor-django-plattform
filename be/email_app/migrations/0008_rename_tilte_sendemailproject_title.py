# Generated by Django 3.2.4 on 2022-07-24 07:25

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('email_app', '0007_auto_20220723_1307'),
    ]

    operations = [
        migrations.RenameField(
            model_name='sendemailproject',
            old_name='tilte',
            new_name='title',
        ),
    ]