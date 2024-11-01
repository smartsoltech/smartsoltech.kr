from django.shortcuts import render, get_object_or_404, redirect
from .models import Service, Project, Client, BlogPost, Review, Order, ServiceRequest
from django.db.models import Avg
from comunication.models import TelegramSettings
import qrcode
import os
from django.conf import settings
import uuid
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.http import JsonResponse
from django.utils.crypto import get_random_string
from django.contrib.auth.models import User
from decouple import config
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from django.core.mail import send_mail
from comunication.telegram_bot import TelegramBot
import hmac
import hashlib
import json
from django.views.decorators.csrf import csrf_exempt
import logging
from django.db import transaction, IntegrityError
from django.db.models import Q

logger = logging.getLogger(__name__)

# Initialize Telegram Bot
try:
    bot = TelegramBot()
except Exception as e:
    logger.error(f"Failed to initialize Telegram bot: {str(e)}")

def home(request):
    services = Service.objects.all()
    return render(request, 'web/home.html', {'services': services})

def service_detail(request, pk):
    service = get_object_or_404(Service, pk=pk)
    projects_in_category = Project.objects.filter(category=service.category)
    average_rating = service.reviews.aggregate(Avg('rating'))['rating__avg'] or 0
    total_reviews = service.reviews.count()
    reviews = service.reviews.all()
    return render(request, 'web/service_detail.html', {
        'service': service,
        'projects_in_category': projects_in_category,
        'average_rating': average_rating,
        'total_reviews': total_reviews,
        'reviews': reviews,
    })

def project_detail(request, pk):
    project = get_object_or_404(Project, pk=pk)
    return render(request, 'web/project_detail.html', {'project': project})

def client_detail(request, pk):
    client = get_object_or_404(Client, pk=pk)
    return render(request, 'web/client_detail.html', {'client': client})

def blog_post_detail(request, pk):
    blog_post = get_object_or_404(BlogPost, pk=pk)
    return render(request, 'web/blog_post_detail.html', {'blog_post': blog_post})

def services_view(request):
    services = Service.objects.all()
    return render(request, 'web/services.html', {'services': services})

def about_view(request):
    return render(request, 'web/about.html')

def create_service_request(request, service_id):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            client_email = data.get('client_email')
            client_phone = data.get('client_phone')
            client_name = data.get('client_name')

            if not all([client_email, client_phone, client_name]):
                return JsonResponse({'status': 'error', 'message': 'Все поля должны быть заполнены'}, status=400)

            service = get_object_or_404(Service, pk=service_id)

            # Проверяем наличие клиента по email (так как email должен быть уникальным)
            client, client_created = Client.objects.get_or_create(
                email=client_email,
                defaults={
                    'first_name': client_name.split()[0] if client_name else "",
                    'last_name': client_name.split()[-1] if len(client_name.split()) > 1 else "",
                    'phone_number': client_phone,
                }
            )

            # Обновляем данные клиента, если он уже существовал (например, телефон или имя изменились)
            if not client_created:
                client.first_name = client_name.split()[0]
                client.last_name = client_name.split()[-1] if len(client_name.split()) > 1 else ""
                client.phone_number = client_phone
                client.save()

            # Проверяем наличие заявки на эту же услугу, не завершенной и не подтвержденной
            existing_requests = ServiceRequest.objects.filter(client=client, service=service, is_verified=False)
            if existing_requests.exists():
                return JsonResponse({
                    'status': 'existing_request',
                    'message': 'У вас уже есть активная заявка на данную услугу. Пожалуйста, проверьте ваш Telegram для завершения процесса.'
                })

            # Создаем новую заявку для клиента
            token = uuid.uuid4().hex
            service_request = ServiceRequest.objects.create(
                service=service,
                client=client,
                token=token,
                is_verified=False
            )

            return JsonResponse({
                'status': 'success',
                'message': 'Заявка успешно создана. Пожалуйста, проверьте ваш Telegram для подтверждения.',
                'service_request_id': service_request.id,
            })

        except json.JSONDecodeError:
            logger.error("Invalid JSON format")
            return JsonResponse({'status': 'error', 'message': 'Неверный формат данных'}, status=400)
    return JsonResponse({'status': 'error', 'message': 'Метод запроса должен быть POST'}, status=405)

def generate_qr_code(request, service_id):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            client_email = data.get('client_email')
            client_phone = data.get('client_phone')
            client_name = data.get('client_name')

            if not all([client_email, client_phone, client_name]):
                logger.error("Все поля должны быть заполнены")
                return JsonResponse({'error': 'Все поля должны быть заполнены'}, status=400)

            # Используем транзакцию для предотвращения конкурентного создания дубликатов
            with transaction.atomic():
                user, user_created = User.objects.select_for_update().get_or_create(
                    email=client_email,
                    defaults={
                        "username": f"{client_email.split('@')[0]}_{get_random_string(5)}",
                        "first_name": client_name.split()[0] if client_name else "",
                        "last_name": client_name.split()[-1] if len(client_name.split()) > 1 else ""
                    }
                )
                if not user_created:
                    # Обновляем информацию о пользователе, если он уже существует
                    user.first_name = client_name.split()[0] if client_name else ""
                    user.last_name = client_name.split()[-1] if len(client_name.split()) > 1 else ""
                    user.save()

                client, client_created = Client.objects.select_for_update().get_or_create(
                    email=client_email,
                    defaults={
                        'user': user,
                        'first_name': user.first_name,
                        'last_name': user.last_name,
                        'phone_number': client_phone
                    }
                )

                if not client_created:
                    # Обновляем информацию о клиенте, если он уже существует
                    client.first_name = user.first_name
                    client.last_name = user.last_name
                    client.phone_number = client_phone
                    client.save()

            # Проверка на существование активной заявки
            service = get_object_or_404(Service, pk=service_id)
            existing_requests = ServiceRequest.objects.filter(client=client, service=service, is_verified=False)
            if existing_requests.exists():
                return JsonResponse({
                    'status': 'existing_request',
                    'message': 'У вас уже есть активная заявка на данную услугу. Пожалуйста, проверьте ваш Telegram для завершения процесса.'
                })

            # Создаем новую заявку на услугу
            token = uuid.uuid4().hex
            service_request = ServiceRequest.objects.create(
                service=service,
                client=client,
                token=token,
                is_verified=False
            )
            logger.info(f"Создана новая заявка: {service_request.id} для клиента: {client.email}")

            # Генерация ссылки и QR-кода для Telegram
            telegram_settings = get_object_or_404(TelegramSettings, pk=1)
            registration_link = f'https://t.me/{telegram_settings.bot_name}?start=request_{service_request.id}_token_{urlsafe_base64_encode(force_bytes(token))}'

            qr = qrcode.make(registration_link)
            qr_code_dir = os.path.join(settings.STATICFILES_DIRS[0], 'qr_codes')
            qr_code_path = os.path.join(qr_code_dir, f"request_{service_request.id}.png")
            external_qr_link = f'static/qr_codes/request_{service_request.id}.png'

            if not os.path.exists(qr_code_dir):
                os.makedirs(qr_code_dir)

            qr.save(qr_code_path)

        except IntegrityError as e:
            logger.error(f"Ошибка целостности данных при создании пользователя или клиента: {str(e)}")
            return JsonResponse({'error': 'Ошибка при обработке данных. Пожалуйста, попробуйте позже.'}, status=500)
        except Exception as e:
            logger.error(f"Ошибка при обработке запроса: {str(e)}")
            return JsonResponse({'error': f'Ошибка: {str(e)}'}, status=500)

        return JsonResponse({
            'registration_link': registration_link,
            'qr_code_url': f"/{external_qr_link}",
            'service_request_id': service_request.id,
            'client_email': client_email,
            'client_phone': client_phone,
            'client_name': client_name
        })
    return JsonResponse({'error': 'Метод запроса должен быть POST'}, status=405)

def request_status(request, service_id):
    try:
        service_request = get_object_or_404(ServiceRequest, pk=service_id)
        client = service_request.client
        is_verified = service_request.is_verified

        return JsonResponse({
            'is_verified': is_verified,
            'client_name': client.first_name if client else "Неизвестно",
            'client_chat_id': client.chat_id if client else None,
        })
    except Exception as e:
        logger.error(f"Ошибка при получении статуса заявки: {str(e)}")
        return JsonResponse({'error': str(e)}, status=500)

@csrf_exempt
def send_telegram_notification(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)

            # Логируем полученные данные для отладки
            logging.info(f"Полученные данные для подтверждения заявки: {data}")

            service_request_id = data.get('service_request_id')
            client_chat_id = data.get('client_chat_id')
            client_name = data.get('client_name')

            if not service_request_id or not client_chat_id:
                return JsonResponse({'error': 'Недостаточно данных для подтверждения'}, status=400)

            # Проверяем существование заявки
            service_request = ServiceRequest.objects.filter(id=service_request_id).first()
            if not service_request:
                return JsonResponse({'error': 'Заявка не найдена'}, status=404)

            # Обновляем заявку с chat_id, если все верно
            service_request.chat_id = client_chat_id
            service_request.is_verified = True
            service_request.save()

            return JsonResponse({'status': 'Уведомление успешно отправлено в Telegram'})

        except json.JSONDecodeError as e:
            logging.error(f"Ошибка при декодировании JSON: {e}")
            return JsonResponse({'error': 'Неверный формат данных'}, status=400)

    logging.error(f"Неподдерживаемый метод запроса: {request.method}")
    return JsonResponse({'error': 'Метод запроса должен быть POST'}, status=405)


def generate_secure_token(service_request_id, secret_key):
    """Генерация безопасного токена для подтверждения подлинности запроса."""
    data = f'{service_request_id}:{secret_key}'
    return hmac.new(secret_key.encode(), data.encode(), hashlib.sha256).hexdigest()

def complete_registration(request, request_id):
    service_request = get_object_or_404(ServiceRequest, pk=request_id)
    if request.method == 'POST':
        client_email = request.POST.get('client_email', service_request.client.email)
        client_phone = request.POST.get('client_phone', service_request.client.phone_number)
        chat_id = request.POST.get('chat_id', service_request.chat_id)

        if not all([client_email, client_phone, chat_id]):
            return JsonResponse({'status': 'error', 'message': 'Все поля должны быть заполнены.'}, status=400)

        client = service_request.client
        client.email = client_email
        client.phone_number = client_phone
        client.save()

        service_request.chat_id = chat_id
        service_request.save()

        return JsonResponse({'status': 'success', 'message': 'Регистрация успешно завершена.'})

    return render(request, 'web/complete_registration.html', {'service_request': service_request})
