# Generated by Django 3.2.12 on 2022-05-23 16:25

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('degreed', '0020_auto_20220405_2311'),
    ]

    operations = [
        migrations.AddField(
            model_name='degreedenterprisecustomerconfiguration',
            name='dry_run_mode_enabled',
            field=models.BooleanField(default=False, help_text='Is this configuration in dry-run mode? (experimental)'),
        ),
        migrations.AddField(
            model_name='historicaldegreedenterprisecustomerconfiguration',
            name='dry_run_mode_enabled',
            field=models.BooleanField(default=False, help_text='Is this configuration in dry-run mode? (experimental)'),
        ),
    ]
