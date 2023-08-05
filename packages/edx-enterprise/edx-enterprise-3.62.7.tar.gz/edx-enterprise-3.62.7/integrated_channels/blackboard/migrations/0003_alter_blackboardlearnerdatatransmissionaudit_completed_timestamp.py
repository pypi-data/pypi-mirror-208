# Generated by Django 3.2.12 on 2022-03-23 17:17

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('blackboard', '0002_auto_20220302_2231'),
    ]

    operations = [
        migrations.AlterField(
            model_name='blackboardlearnerdatatransmissionaudit',
            name='completed_timestamp',
            field=models.CharField(blank=True, help_text='Represents the Blackboard representation of a timestamp: yyyy-mm-dd, which is always 10 characters. Can be left unset for audit transmissions.', max_length=10, null=True),
        ),
    ]
