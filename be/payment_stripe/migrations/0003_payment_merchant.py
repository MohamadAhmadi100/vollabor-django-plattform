# Generated by Django 3.2.4 on 2022-08-16 11:07

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('payment_stripe', '0002_payment_invoice'),
    ]

    operations = [
        migrations.AddField(
            model_name='payment',
            name='merchant',
            field=models.CharField(max_length=36, null=True),
        ),
    ]