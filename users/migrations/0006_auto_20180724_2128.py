# Generated by Django 2.0.6 on 2018-07-24 21:28

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0005_auto_20180724_1120'),
    ]

    operations = [
        migrations.RenameField(
            model_name='merchant',
            old_name='name_key',
            new_name='name_code',
        ),
    ]
