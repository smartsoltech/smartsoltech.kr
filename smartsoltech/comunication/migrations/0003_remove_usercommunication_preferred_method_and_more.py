# Generated by Django 5.1.1 on 2024-10-08 12:49

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('comunication', '0002_emailsettings_telegramsettings'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='usercommunication',
            name='preferred_method',
        ),
        migrations.RemoveField(
            model_name='usercommunication',
            name='user',
        ),
        migrations.DeleteModel(
            name='CommunicationMethod',
        ),
        migrations.DeleteModel(
            name='UserCommunication',
        ),
    ]
