# Generated by Django 2.0.8 on 2018-08-07 11:17

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('wxapp', '0015_auto_20180807_1047'),
    ]

    operations = [
        migrations.AddField(
            model_name='wxpaymentorder',
            name='prepay_refresh_at',
            field=models.DateTimeField(auto_now_add=True, default=django.utils.timezone.now, verbose_name='prepay_id 刷新时间'),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='wxmchuser',
            name='token_refresh_at',
            field=models.DateTimeField(auto_now_add=True, verbose_name='access_token凭证更新时间'),
        ),
    ]