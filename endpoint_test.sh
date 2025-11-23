#!/bin/bash

BASE_URL="http://localhost:8002/auth"
EMAIL="testuser@example.com"
PASSWORD="secret123"

echo "1️⃣ Регистрация пользователя..."
curl -s -X POST "$BASE_URL/register" \
  -H "Content-Type: application/json" \
  -d "{\"email\": \"$EMAIL\", \"password\": \"$PASSWORD\"}" | tee response_register.json
echo -e "\n"

USER_ID=$(jq .id response_register.json)

echo "2️⃣ Аутентификация..."
curl -s -X POST "$BASE_URL/login" \
  -H "Content-Type: application/json" \
  -d "{\"email\": \"$EMAIL\", \"password\": \"$PASSWORD\"}" | tee response_login.json
echo -e "\n"

TOKEN=$(jq -r .access_token response_login.json)

echo "🔐 Получен токен: $TOKEN"
AUTH_HEADER="Authorization: Bearer $TOKEN"

echo "3️⃣ Получение текущего пользователя (/me)..."
curl -s -X GET "$BASE_URL/me" -H "$AUTH_HEADER" | tee response_me.json
echo -e "\n"

echo "4️⃣ Получение списка всех пользователей..."
curl -s -X GET "$BASE_URL/users" | tee response_users.json
echo -e "\n"

echo "5️⃣ Получение пользователя по ID ($USER_ID)..."
curl -s -X GET "$BASE_URL/users/$USER_ID" | tee response_user.json
echo -e "\n"

echo "6️⃣ Обновление пользователя..."
curl -s -X PUT "$BASE_URL/users/$USER_ID" \
  -H "Content-Type: application/json" \
  -d "{\"email\": \"updated_$EMAIL\", \"role\": \"admin\"}" | tee response_update.json
echo -e "\n"

echo "7️⃣ Удаление пользователя..."
curl -s -X DELETE "$BASE_URL/users/$USER_ID" | tee response_delete.json
echo -e "\n"

echo "✅ Тест завершён."
