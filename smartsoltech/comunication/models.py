# communication/models.py
from django.db import models
from django.contrib.auth.models import User
from web.models import Client
    
class EmailSettings(models.Model):
    smtp_server = models.CharField(max_length=255)
    smtp_port = models.PositiveIntegerField()
    sender_email = models.EmailField()
    password = models.CharField(max_length=255)
    use_tls = models.BooleanField(default=True)
    use_ssl = models.BooleanField(default=False)
    display_name = models.CharField(max_length=255, null=True, blank=True)

    def __str__(self):
        return f"SMTP: {self.smtp_server}, Email: {self.sender_email}"
    class Meta:
        verbose_name = 'Параметры E-mail'
        verbose_name_plural = 'Параметры E-mail'
        ordering = ['-display_name']
        
class TelegramSettings(models.Model):
    bot_name = models.CharField(max_length=100)
    bot_token = models.CharField(max_length=255)
    webhook_url = models.URLField(null=True, blank=True)
    use_polling = models.BooleanField(default=True)

    def __str__(self):
        return f"Telegram Bot: {self.bot_name}"
    class Meta:
        verbose_name = 'Параметры Telegram бота'
        verbose_name_plural = 'Параметры Telegram ботов'
        ordering = ['-bot_name']
class UserCommunication(models.Model):
    client = models.ForeignKey(
        'web.Client', on_delete=models.CASCADE, related_name='communications', verbose_name='Клиент', null=True, blank=True
    )
    email = models.EmailField(verbose_name='Электронная почта')
    phone = models.CharField(max_length=15, blank=True, verbose_name='Телефон')
    chat_id = models.CharField(max_length=50, blank=True, verbose_name='Telegram Chat ID')

    class Meta:
        verbose_name = 'Связь с клиентом'
        verbose_name_plural = 'Связи с клиентами'
        ordering = ['-id']

    def __str__(self):
        if self.client:
            return f"Связь с клиентом: {self.client.first_name} {self.client.last_name} ({self.email})"
        return f"Связь без клиента ({self.email})"
