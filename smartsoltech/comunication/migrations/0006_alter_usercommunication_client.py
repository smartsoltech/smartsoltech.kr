# Generated by Django 5.1.1 on 2024-10-13 04:20

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('comunication', '0005_alter_emailsettings_options_and_more'),
        ('web', '0005_alter_blogpost_options_alter_category_options_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='usercommunication',
            name='client',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='communications', to='web.client', verbose_name='Клиент'),
        ),
    ]
