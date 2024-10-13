# comunication/management/commands/start_telegram_bot.py
from django.core.management.base import BaseCommand
from comunication.telegram_bot import TelegramBot

class Command(BaseCommand):
    help = 'Starts the Telegram bot'

    def handle(self, *args, **kwargs):
        bot = TelegramBot()
        self.stdout.write('Starting Telegram bot polling...')
        bot.start_bot_polling()