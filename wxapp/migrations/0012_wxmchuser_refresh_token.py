# Generated by Django 2.0.6 on 2018-07-30 17:44

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('wxapp', '0011_auto_20180728_1611'),
    ]

    operations = [
        migrations.AddField(
            model_name='wxmchuser',
            name='refresh_token',
            field=models.CharField(max_length=255, null=True, verbose_name='授权刷新凭证'),
        ),
    ]