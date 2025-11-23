import logging
import json
import requests
import os
import base64
import re
from comunication.models import TelegramSettings
from web.models import ServiceRequest, Order, Project, Client, User
import telebot
from django.shortcuts import get_object_or_404
from django.utils.crypto import get_random_string

class TelegramBot:
    def __init__(self):
        # Получение настроек бота из базы данных
        bot_settings = TelegramSettings.objects.first()
        if bot_settings and bot_settings.bot_token:
            TELEGRAM_BOT_TOKEN = bot_settings.bot_token.strip()
            
            # Проверяем валидность токена
            if self._validate_token(TELEGRAM_BOT_TOKEN):
                self.bot = telebot.TeleBot(TELEGRAM_BOT_TOKEN)
                logging.info(f"[TelegramBot] Бот инициализирован с токеном для {bot_settings.bot_name}.")
            else:
                logging.error(f"[TelegramBot] Токен невалиден: {TELEGRAM_BOT_TOKEN[:10]}...")
                raise Exception(f"Невалидный токен Telegram бота. Обновите токен в базе данных.")
        else:
            raise Exception("Telegram bot settings not found or token is empty")

    def _validate_token(self, token):
        """Проверяет валидность токена через Telegram API"""
        url = f"https://api.telegram.org/bot{token}/getMe"
        try:
            response = requests.get(url, timeout=10)
            result = response.json()
            if result.get('ok'):
                bot_info = result.get('result', {})
                logging.info(f"[TelegramBot] Токен валиден. Бот: @{bot_info.get('username', 'unknown')}")
                return True
            else:
                logging.error(f"[TelegramBot] Ошибка Telegram API: {result.get('description', 'Unknown error')}")
                return False
        except requests.RequestException as e:
            logging.error(f"[TelegramBot] Ошибка при проверке токена: {e}")
            return False

    def start_bot_polling(self):
        logging.info("[TelegramBot] Бот начал работу в режиме polling.")

        @self.bot.message_handler(commands=['start'])
        def send_welcome(message):
            # Проверяем, содержатся ли параметры в команде /start
            match = re.match(r'/start request_(\d+)_token_(.*)', message.text)
            logging.info(f"[TelegramBot] Получена команда /start: {message.text}")

            if match:
                self.handle_confirm_command(message, match)
            elif message.text.strip() == '/start':
                # Ответ на просто команду /start без параметров
                self.bot.reply_to(message, "Здравствуйте! Пожалуйста, используйте команду /start с корректными параметрами для подтверждения регистрации.")
            else:
                self.bot.reply_to(message, "Здравствуйте! Пожалуйста, используйте команду /start с корректными параметрами для подтверждения регистрации.")

        @self.bot.message_handler(func=lambda message: 'статус заявки' in message.text.lower())
        def handle_service_request_status(message):
            chat_id = message.chat.id
            client = Client.objects.filter(chat_id=chat_id).first()
            if client:
                service_requests = ServiceRequest.objects.filter(client=client)
                if service_requests.exists():
                    response = "Ваши заявки:\n"
                    for req in service_requests:
                        response += (
                            f"Номер заявки: {req.id}\n"
                            f"Услуга: {req.service.name}\n"
                            f"Дата создания: {req.created_at.strftime('%Y-%m-%d')}\n"
                            f"UID заявки: {req.token}\n"
                            f"Подтверждена: {'Да' if req.is_verified else 'Нет'}\n\n"
                        )
                else:
                    response = "У вас нет активных заявок."
            else:
                response = "Клиент не найден. Пожалуйста, зарегистрируйтесь."
            self.bot.reply_to(message, response)

        @self.bot.message_handler(func=lambda message: 'статус заказа' in message.text.lower())
        def handle_order_status(message):
            chat_id = message.chat.id
            client = Client.objects.filter(chat_id=chat_id).first()
            if client:
                orders = Order.objects.filter(client=client)
                if orders.exists():
                    response = "Ваши заказы:\n"
                    for order in orders:
                        response += (
                            f"Номер заказа: {order.id}\n"
                            f"Услуга: {order.service.name}\n"
                            f"Статус: {order.get_status_display()}\n\n"
                        )
                else:
                    response = "У вас нет активных заказов."
            else:
                response = "Клиент не найден. Пожалуйста, зарегистрируйтесь."
            self.bot.reply_to(message, response)

        @self.bot.message_handler(func=lambda message: 'статус проекта' in message.text.lower())
        def handle_project_status(message):
            chat_id = message.chat.id
            client = Client.objects.filter(chat_id=chat_id).first()
            if client:
                projects = Project.objects.filter(order__client=client)
                if projects.exists():
                    response = "Ваши проекты:\n"
                    for project in projects:
                        response += (
                            f"Номер проекта: {project.id}\n"
                            f"Название проекта: {project.name}\n"
                            f"Статус: {project.get_status_display()}\n"
                            f"Дата завершения: {project.completion_date.strftime('%Y-%m-%d') if project.completion_date else 'В процессе'}\n\n"
                        )
                else:
                    response = "У вас нет активных проектов."
            else:
                response = "Клиент не найден. Пожалуйста, зарегистрируйтесь."
            self.bot.reply_to(message, response)
            

        # Запуск бота
        try:
            self.bot.polling(non_stop=True)
        except Exception as e:
            logging.error(f"[TelegramBot] Ошибка при запуске polling: {e}")

    def handle_confirm_command(self, message, match=None):
        chat_id = message.chat.id
        logging.info(f"[TelegramBot] Получено сообщение для подтверждения: {message.text}")

        if not match:
            match = re.match(r'/start request_(\d+)_token_(.*)', message.text)

        if match:
            request_id = match.group(1)
            encoded_token = match.group(2)

            # Декодируем токен
            try:
                token = base64.urlsafe_b64decode(encoded_token + '==').decode('utf-8')
                logging.info(f"[TelegramBot] Декодированный токен: {token}")
            except Exception as e:
                logging.error(f"[TelegramBot] Ошибка при декодировании токена: {e}")
                self.bot.send_message(chat_id, "Ошибка: Некорректный токен. Пожалуйста, повторите попытку позже.")
                return

            # Получаем заявку
            try:
                service_request = ServiceRequest.objects.get(id=request_id, token=token)
                logging.info(f"[TelegramBot] Заявка найдена: {service_request}")
            except ServiceRequest.DoesNotExist:
                logging.error(f"[TelegramBot] Заявка с id {request_id} и токеном {token} не найдена.")
                self.bot.send_message(chat_id, "Ошибка: Неверная заявка или токен. Пожалуйста, проверьте ссылку.")
                return

            # Если заявка найдена, обновляем и подтверждаем клиента
            if service_request:
                service_request.chat_id = chat_id
                service_request.is_verified = True  # Обновляем статус на подтвержденный
                service_request.save()
                logging.info(f"[TelegramBot] Заявка {service_request.id} подтверждена и обновлена.")

                # Обновляем или создаем клиента, связанного с заявкой
                client = service_request.client

                # Проверяем, существует ли связанный пользователь, если нет — создаем его
                if not client.user:
                    user, created = User.objects.get_or_create(
                        email=client.email,
                        defaults={
                            'username': f"{client.email.split('@')[0]}_{get_random_string(5)}",
                            'first_name': message.from_user.first_name,
                            'last_name': message.from_user.last_name if message.from_user.last_name else ''
                        }
                    )

                    if not created:
                        # Если пользователь уже существовал, обновляем его данные
                        user.first_name = message.from_user.first_name
                        if message.from_user.last_name:
                            user.last_name = message.from_user.last_name
                        user.save()
                        logging.info(f"[TelegramBot] Обновлен пользователь {user.username} с данными из Телеграм.")

                    # Связываем клиента с пользователем
                    client.user = user
                    client.save()

                else:
                    # Обновляем данные существующего пользователя
                    user = client.user
                    user.first_name = message.from_user.first_name
                    if message.from_user.last_name:
                        user.last_name = message.from_user.last_name
                    user.save()
                    logging.info(f"[TelegramBot] Пользователь {user.username} обновлен с данными из Телеграм.")

                # Обновляем chat_id клиента
                client.chat_id = chat_id
                client.save()
                logging.info(f"[TelegramBot] Клиент {client.id} обновлен с chat_id {chat_id}")

                # Отправляем сообщение пользователю в Telegram с подтверждением и информацией о заявке
                confirmation_message = (
                    f"Здравствуйте, {client.first_name}!\n\n"
                    f"Ваш аккаунт успешно подтвержден! 🎉\n\n"
                    f"Детали вашей заявки:\n"
                    f"Номер заявки: {service_request.id}\n"
                    f"Услуга: {service_request.service.name}\n"
                    f"Статус заявки: {'Подтверждена' if service_request.is_verified else 'Не подтверждена'}\n"
                    f"Дата создания: {service_request.created_at.strftime('%Y-%m-%d %H:%M:%S')}\n"
                    f"Спасибо, что выбрали наши услуги! Если у вас возникнут вопросы, вы всегда можете обратиться к нам."
                )
                self.bot.send_message(chat_id, confirmation_message)

                # Вместо дополнительного POST-запроса — сообщаем о подтверждении через сообщение
                self.bot.send_message(chat_id, "Ваш аккаунт успешно подтвержден на сервере! Продолжайте на сайте.")

            else:
                self.bot.send_message(chat_id, "Ошибка: Неверная заявка или токен. Пожалуйста, проверьте ссылку.")
        else:
            response_message = "Ошибка: Некорректная команда. Пожалуйста, используйте ссылку, предоставленную на сайте для регистрации."
            self.bot.send_message(chat_id, response_message)


