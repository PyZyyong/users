# Generated by Django 2.0.6 on 2018-07-24 11:20

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0004_auto_20180724_1034'),
    ]

    operations = [
        migrations.AlterField(
            model_name='merchantcertificate',
            name='codename',
            field=models.CharField(blank=True, max_length=50, null=True, verbose_name='编码'),
        ),
        migrations.AlterField(
            model_name='merchantcertificate',
            name='extra_data1',
            field=models.CharField(blank=True, max_length=100, null=True, verbose_name='额外信息'),
        ),
        migrations.AlterField(
            model_name='merchantcertificate',
            name='name',
            field=models.CharField(blank=True, max_length=20, null=True, verbose_name='名称'),
        ),
        migrations.AlterField(
            model_name='merchantcertificate',
            name='no',
            field=models.CharField(blank=True, max_length=50, null=True, verbose_name='证书编号'),
        ),
        migrations.AlterField(
            model_name='merchantlegalperson',
            name='idcard_number',
            field=models.CharField(blank=True, max_length=20, null=True, verbose_name='身份证号'),
        ),
        migrations.AlterField(
            model_name='merchantlegalperson',
            name='realname',
            field=models.CharField(blank=True, max_length=10, null=True, verbose_name='法人姓名'),
        ),
    ]
