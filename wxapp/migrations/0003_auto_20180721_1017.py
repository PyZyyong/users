# Generated by Django 2.0.6 on 2018-07-21 10:17

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('wxapp', '0002_auto_20180720_1932'),
    ]

    operations = [
        migrations.AlterField(
            model_name='wxpaymentorder',
            name='time_end',
            field=models.CharField(max_length=255, null=True, verbose_name='支付完成时间'),
        ),
    ]