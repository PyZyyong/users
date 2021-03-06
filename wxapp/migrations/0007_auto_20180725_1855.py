# Generated by Django 2.0.6 on 2018-07-25 18:55

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('wxapp', '0006_auto_20180724_1831'),
    ]

    operations = [
        migrations.AlterField(
            model_name='wxmchuser',
            name='app_id',
            field=models.CharField(max_length=100, null=True, verbose_name='小程序id'),
        ),
        migrations.AlterField(
            model_name='wxmchuser',
            name='app_secret',
            field=models.CharField(max_length=100, null=True, verbose_name='小程序密钥'),
        ),
        migrations.AlterField(
            model_name='wxmchuser',
            name='shop_id',
            field=models.CharField(max_length=100, null=True, verbose_name='小程序标识'),
        ),
    ]
