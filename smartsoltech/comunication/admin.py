# communication/admin.py
from django.contrib import admin
from .models import EmailSettings, TelegramSettings, UserCommunication

@admin.register(EmailSettings)
class EmailSettingsAdmin(admin.ModelAdmin):
    list_display = ('smtp_server', 'sender_email', 'use_tls', 'use_ssl')

@admin.register(TelegramSettings)
class TelegramSettingsAdmin(admin.ModelAdmin):
    list_display = ('bot_name', 'bot_token', 'use_polling')
    
@admin.register(UserCommunication)
class UserCommunicationAdmin(admin.ModelAdmin):
    list_display = ('client', 'email', 'phone', 'chat_id')
    