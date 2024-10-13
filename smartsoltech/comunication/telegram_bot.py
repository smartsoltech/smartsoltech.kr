# import telebot
# from decouple import config
# from django.shortcuts import get_object_or_404
# from web.models import Client, ServiceRequest, Order
# from comunication.models import TelegramSettings
# import re
# import base64
# import logging

# class TelegramBot:
#     def __init__(self):
#         # Get bot settings from the database
#         bot_settings = TelegramSettings.objects.first()
#         if bot_settings:
#             TELEGRAM_BOT_TOKEN = bot_settings.bot_token
#             self.bot = telebot.TeleBot(TELEGRAM_BOT_TOKEN)
#         else:
#             raise Exception("Telegram bot settings not found")

#     def start_bot_polling(self):
#         @self.bot.message_handler(commands=['start'])
#         def send_welcome(message):
#             # Проверяем, содержатся ли параметры в команде /start
#             match = re.match(r'/start request_(\d+)_token_(.*)', message.text)
#             if match:
#                 self.handle_confirm_command(message, match)
#             elif message.text.strip() == '/start':
#                 self.bot.reply_to(message, "Ошибка: Некорректная команда. Пожалуйста, используйте ссылку, предоставленную на сайте для регистрации.")
#             else:
#                 self.bot.reply_to(message, "Здравствуйте! Чем я могу помочь? Вы можете задать вопросы о статусе заявки или заказе.")

#         @self.bot.message_handler(func=lambda message: 'статус заявки' in message.text.lower())
#         def handle_service_request_status(message):
#             chat_id = message.chat.id
#             client = Client.objects.filter(chat_id=chat_id).first()
#             if client:
#                 service_requests = ServiceRequest.objects.filter(client_email=client.email)
#                 if service_requests.exists():
#                     response = "Ваши заявки:\n"
#                     for req in service_requests:
#                         response += f"Номер заявки: {req.id}, Услуга: {req.service.name}, Дата создания: {req.created_at.strftime('%d-%m-%Y')}\n"
#                 else:
#                     response = "У вас нет активных заявок."
#             else:
#                 response = "Клиент не найден. Пожалуйста, зарегистрируйтесь."
#             self.bot.reply_to(message, response)

#         @self.bot.message_handler(func=lambda message: 'статус заказа' in message.text.lower())
#         def handle_order_status(message):
#             chat_id = message.chat.id
#             client = Client.objects.filter(chat_id=chat_id).first()
#             if client:
#                 orders = Order.objects.filter(client=client)
#                 if orders.exists():
#                     response = "Ваши заказы:\n"
#                     for order in orders:
#                         response += f"Номер заказа: {order.id}, Услуга: {order.service.name}, Статус: {order.get_status_display()}\n"
#                 else:
#                     response = "У вас нет активных заказов."
#             else:
#                 response = "Клиент не найден. Пожалуйста, зарегистрируйтесь."
#             self.bot.reply_to(message, response)

#         self.bot.polling(non_stop=True)

#     def handle_confirm_command(self, message, match=None):
#         chat_id = message.chat.id
#         if not match:
#             match = re.match(r'/start request_(\d+)_token_(.*)', message.text)
#         if match:
#             request_id = match.group(1)
#             encoded_token = match.group(2)

#             # Декодируем токен из base64
#             try:
#                 token = base64.urlsafe_b64decode(encoded_token + '==').decode('utf-8')
#                 logging.info(f"Декодированный токен: {token}")
#             except Exception as e:
#                 logging.error(f"Ошибка при декодировании токена: {e}")
#                 self.bot.send_message(chat_id, "Ошибка: Некорректный токен. Пожалуйста, повторите попытку позже.")
#                 return

#             # Получаем заявку по ID и токену
#             service_request = ServiceRequest.objects.filter(id=request_id, token=token).first()
#             if service_request:
#                 # Обновляем chat_id клиента
#                 service_request.chat_id = chat_id
#                 service_request.client_name = message.from_user.first_name
#                 service_request.save()

#                 response_message = (
#                     f"Здравствуйте, {message.from_user.first_name}!\n"
#                     f"Ваша заявка на услугу успешно зарегистрирована. "
#                     f"Пожалуйста, вернитесь на сайт для продолжения оформления."
#                 )
#             else:
#                 response_message = "Ошибка: Неверная заявка или токен. Пожалуйста, проверьте ссылку."

#             self.bot.send_message(chat_id, response_message)
#         else:
#             response_message = "Ошибка: Некорректная команда. Пожалуйста, используйте ссылку, предоставленную на сайте для регистрации."
#             self.bot.send_message(chat_id, response_message)

#     def send_telegram_message(self, client_id, service_request_id, custom_message, order_id=None):
#         # Get the client and service request from the database
#         client = get_object_or_404(Client, pk=client_id)
#         service_request = get_object_or_404(ServiceRequest, pk=service_request_id)
#         chat_id = client.chat_id

#         # Build the message content
#         message = f"Здравствуйте, {client.first_name} {client.last_name}!\n"
#         message += custom_message

#         if order_id:
#             order = get_object_or_404(Order, pk=order_id)
#             message += f"\n\nДетали заказа:\nУслуга: {order.service.name}\nСтатус: {order.get_status_display()}\n"
        
#         # Add service request details
#         message += f"\nНомер заявки: {service_request.id}\nДата создания заявки: {service_request.created_at.strftime('%d-%m-%Y')}\n"

#         # Send the message using the bot
#         try:
#             self.bot.send_message(chat_id, message)
#         except Exception as e:
#             logging.error(f"Ошибка при отправке сообщения в Telegram: {e}")


import telebot
from decouple import config
from django.shortcuts import get_object_or_404
from web.models import Client, ServiceRequest, Order
from comunication.models import TelegramSettings
import re
import base64
import logging

class TelegramBot:
    def __init__(self):
        # Get bot settings from the database
        bot_settings = TelegramSettings.objects.first()
        if bot_settings:
            TELEGRAM_BOT_TOKEN = bot_settings.bot_token
            self.bot = telebot.TeleBot(TELEGRAM_BOT_TOKEN)
        else:
            raise Exception("Telegram bot settings not found")

    def start_bot_polling(self):
        @self.bot.message_handler(commands=['start'])
        def send_welcome(message):
            # Проверяем, содержатся ли параметры в команде /start
            match = re.match(r'/start request_(\d+)_token_(.*)', message.text)
            if match:
                self.handle_confirm_command(message, match)
            elif message.text.strip() == '/start':
                self.bot.reply_to(message, "Ошибка: Некорректная команда. Пожалуйста, используйте ссылку, предоставленную на сайте для регистрации.")
            else:
                self.bot.reply_to(message, "Здравствуйте! Пожалуйста, используйте команду /start с корректными параметрами для подтверждения регистрации.")

        @self.bot.message_handler(func=lambda message: 'статус заявки' in message.text.lower())
        def handle_service_request_status(message):
            chat_id = message.chat.id
            client = Client.objects.filter(chat_id=chat_id).first()
            if client:
                service_requests = ServiceRequest.objects.filter(client_email=client.email)
                if service_requests.exists():
                    response = "Ваши заявки:\n"
                    for req in service_requests:
                        response += f"Номер заявки: {req.id}, Услуга: {req.service.name}, Дата создания: {req.created_at.strftime('%d-%m-%Y')}\n"
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
                        response += f"Номер заказа: {order.id}, Услуга: {order.service.name}, Статус: {order.get_status_display()}\n"
                else:
                    response = "У вас нет активных заказов."
            else:
                response = "Клиент не найден. Пожалуйста, зарегистрируйтесь."
            self.bot.reply_to(message, response)

        self.bot.polling(non_stop=True)

    def handle_confirm_command(self, message, match=None):
        chat_id = message.chat.id
        if not match:
            match = re.match(r'/start request_(\d+)_token_(.*)', message.text)
        if match:
            request_id = match.group(1)
            encoded_token = match.group(2)

            # Декодируем токен из base64
            try:
                token = base64.urlsafe_b64decode(encoded_token + '==').decode('utf-8')
                logging.info(f"Декодированный токен: {token}")
            except Exception as e:
                logging.error(f"Ошибка при декодировании токена: {e}")
                self.bot.send_message(chat_id, "Ошибка: Некорректный токен. Пожалуйста, повторите попытку позже.")
                return

            # Получаем заявку по ID и токену
            service_request = ServiceRequest.objects.filter(id=request_id, token=token).first()
            if service_request:
                # Обновляем chat_id клиента
                service_request.chat_id = chat_id
                service_request.client_name = message.from_user.first_name
                service_request.save()

                response_message = (
                    f"Здравствуйте, {message.from_user.first_name}!\n"
                    f"Ваш Telegram аккаунт успешно подтвержден. Пожалуйста, вернитесь на сайт для заполнения остальных данных."
                )
            else:
                response_message = "Ошибка: Неверная заявка или токен. Пожалуйста, проверьте ссылку."

            self.bot.send_message(chat_id, response_message)
        else:
            response_message = "Ошибка: Некорректная команда. Пожалуйста, используйте ссылку, предоставленную на сайте для регистрации."
            self.bot.send_message(chat_id, response_message)

    def send_telegram_message(self, client_id, service_request_id, custom_message, order_id=None):
        # Get the client and service request from the database
        client = get_object_or_404(Client, pk=client_id)
        service_request = get_object_or_404(ServiceRequest, pk=service_request_id)
        chat_id = client.chat_id

        # Build the message content
        message = f"Здравствуйте, {client.first_name} {client.last_name}!\n"
        message += custom_message

        if order_id:
            order = get_object_or_404(Order, pk=order_id)
            message += f"\n\nДетали заказа:\nУслуга: {order.service.name}\nСтатус: {order.get_status_display()}\n"
        
        # Add service request details
        message += f"\nНомер заявки: {service_request.id}\nДата создания заявки: {service_request.created_at.strftime('%d-%m-%Y')}\n"

        # Send the message using the bot
        try:
            self.bot.send_message(chat_id, message)
        except Exception as e:
            logging.error(f"Ошибка при отправке сообщения в Telegram: {e}")

# Example usage:
# bot = TelegramBot()
# bot.start_bot_polling()
# bot.send_telegram_message(client_id=1, service_request_id=1, custom_message="Ваши данные для входа на сайт.")