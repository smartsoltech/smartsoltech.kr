# Generated by Django 5.1.1 on 2024-10-14 11:10

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('web', '0005_alter_blogpost_options_alter_category_options_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='order',
            name='service_request',
            field=models.OneToOneField(default=1, on_delete=django.db.models.deletion.CASCADE, related_name='related_order', to='web.servicerequest'),
            preserve_default=False,
        ),
    ]
