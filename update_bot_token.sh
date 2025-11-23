#!/bin/bash
# Скрипт для обновления токена Telegram бота
# Использование: ./update_bot_token.sh "НОВЫЙ_ТОКЕН"

if [ $# -eq 0 ]; then
    echo "❌ Ошибка: Необходимо указать токен"
    echo "Использование: $0 \"НОВЫЙ_ТОКЕН\""
    echo ""
    echo "Пример: $0 \"1234567890:ABCDEFghijklmnopqrstuvwxyz\""
    echo ""
    echo "Получите токен от @BotFather в Telegram:"
    echo "1. Отправьте /mybots"
    echo "2. Выберите своего бота"
    echo "3. Нажмите 'API Token'"
    exit 1
fi

NEW_TOKEN="$1"

echo "🔄 Обновление токена Telegram бота..."

# Проверяем валидность токена
echo "🔍 Проверка валидности токена..."
RESPONSE=$(curl -s "https://api.telegram.org/bot${NEW_TOKEN}/getMe")
if echo "$RESPONSE" | grep -q '"ok":true'; then
    BOT_USERNAME=$(echo "$RESPONSE" | grep -o '"username":"[^"]*"' | cut -d'"' -f4)
    echo "✅ Токен валиден! Бот: @${BOT_USERNAME}"
else
    echo "❌ Ошибка: Токен невалиден!"
    echo "Ответ API: $RESPONSE"
    exit 1
fi

# Обновляем токен в базе данных
echo "💾 Обновление токена в базе данных..."
docker exec postgres_db psql -U trevor -d 2st_db -c "
UPDATE comunication_telegramsettings 
SET bot_token = '$NEW_TOKEN', bot_name = '@${BOT_USERNAME}' 
WHERE id = 1;
"

if [ $? -eq 0 ]; then
    echo "✅ Токен успешно обновлен в базе данных!"
    echo "🔄 Перезапуск контейнера telegram_bot..."
    docker restart telegram_bot
    echo "🎉 Готово! Проверьте логи: docker logs telegram_bot"
else
    echo "❌ Ошибка при обновлении базы данных"
    exit 1
fi