# Generated by Django 2.0.6 on 2018-07-20 19:32

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('wxapp', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='wxpaymentorder',
            name='time_expire',
            field=models.CharField(max_length=255, null=True, verbose_name='交易结束时间'),
        ),
        migrations.AlterField(
            model_name='wxpaymentorder',
            name='time_start',
            field=models.CharField(max_length=255, null=True, verbose_name='交易起始时间'),
        ),
    ]