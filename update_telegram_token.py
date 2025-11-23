#!/usr/bin/env python3
"""
Скрипт для обновления токена Telegram бота в базе данных
"""
import os
import sys
import django
import requests

# Настройка Django
sys.path.append('/app/smartsoltech')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'smartsoltech.settings')
django.setup()

from comunication.models import TelegramSettings

def validate_token(token):
    """Проверяет валидность токена через Telegram API"""
    url = f"https://api.telegram.org/bot{token}/getMe"
    try:
        response = requests.get(url, timeout=10)
        return response.json().get('ok', False)
    except requests.RequestException:
        return False

def update_telegram_token(new_token, bot_name=None):
    """Обновляет токен Telegram бота в базе данных"""
    
    # Проверяем валидность токена
    if not validate_token(new_token):
        print(f"❌ Ошибка: Токен {new_token} невалиден!")
        return False
    
    # Получаем информацию о боте
    url = f"https://api.telegram.org/bot{new_token}/getMe"
    response = requests.get(url)
    bot_info = response.json()
    
    if bot_info.get('ok'):
        bot_username = bot_info['result']['username']
        print(f"✅ Токен валиден. Бот: @{bot_username}")
        
        # Обновляем настройки в базе данных
        telegram_settings, created = TelegramSettings.objects.get_or_create(
            id=1,
            defaults={
                'bot_name': f"@{bot_username}",
                'bot_token': new_token,
                'use_polling': True
            }
        )
        
        if not created:
            telegram_settings.bot_token = new_token
            telegram_settings.bot_name = bot_name or f"@{bot_username}"
            telegram_settings.save()
            print(f"✅ Токен обновлен в базе данных для бота {telegram_settings.bot_name}")
        else:
            print(f"✅ Создана новая запись для бота @{bot_username}")
        
        return True
    else:
        print(f"❌ Ошибка при получении информации о боте")
        return False

if __name__ == "__main__":
    print("🤖 Скрипт обновления токена Telegram бота")
    print("=" * 50)
    
    # Проверяем текущий токен
    try:
        current_settings = TelegramSettings.objects.first()
        if current_settings:
            print(f"Текущий бот: {current_settings.bot_name}")
            print(f"Текущий токен: {current_settings.bot_token[:10]}...")
            
            if not validate_token(current_settings.bot_token):
                print("❌ Текущий токен невалиден")
            else:
                print("✅ Текущий токен валиден")
        else:
            print("⚠️ Настройки Telegram бота не найдены")
    except Exception as e:
        print(f"❌ Ошибка при проверке текущих настроек: {e}")
    
    print("\n" + "=" * 50)
    print("Для обновления токена:")
    print("1. Идите к @BotFather в Telegram")
    print("2. Создайте нового бота или используйте /token для существующего")
    print("3. Скопируйте токен и введите его ниже")
    print("=" * 50)
    
    new_token = input("\nВведите новый токен бота (или 'exit' для выхода): ").strip()
    
    if new_token.lower() == 'exit':
        print("Выход...")
        sys.exit(0)
    
    if update_telegram_token(new_token):
        print("\n🎉 Токен успешно обновлен!")
        print("Теперь перезапустите контейнер telegram_bot:")
        print("docker restart telegram_bot")
    else:
        print("\n❌ Не удалось обновить токен")