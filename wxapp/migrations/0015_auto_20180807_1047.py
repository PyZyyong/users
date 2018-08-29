# Generated by Django 2.0.8 on 2018-08-07 10:47

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('wxapp', '0014_auto_20180801_2044'),
    ]

    operations = [
        migrations.AlterField(
            model_name='wxpaymentorder',
            name='time_expire',
            field=models.DateTimeField(null=True, verbose_name='交易结束时间'),
        ),
        migrations.AlterField(
            model_name='wxpaymentorder',
            name='time_start',
            field=models.DateTimeField(null=True, verbose_name='交易起始时间'),
        ),
    ]
