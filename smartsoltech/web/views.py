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
from django.utils.crypto import get_random_string  # Импорт get_random_string
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

# sens
try:
    bot = TelegramBot()
except Exception as e:
    print (e)

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

# def create_service_request(request, service_id):
#     service = get_object_or_404(Service, pk=service_id)
#     if request.method == 'POST':
#         client_name = request.POST.get('client_name')
#         client_email = request.POST.get('client_email')
#         client_phone = request.POST.get('client_phone')
#         description = request.POST.get('description')
#         chat_id = request.POST.get('chat_id')
#         token = uuid.uuid4().hex

#         # Создаем заявку
#         service_request = ServiceRequest.objects.create(
#             service=service,
#             client_name=client_name,
#             client_email=client_email,
#             client_phone=client_phone,
#             chat_id=chat_id,
#             token=token
#         )

#         # Генерация уникальных данных для пользователя
#         username = f"{client_email.split('@')[0]}_{get_random_string(5)}"
#         password = get_random_string(8)

#         # Создание пользователя
#         user = User.objects.create_user(username=username, password=password)
#         user.first_name = client_name.split()[0] if client_name else ""
#         user.last_name = client_name.split()[-1] if len(client_name.split()) > 1 else ""
#         user.email = client_email
#         user.save()

#         # Создание клиента и привязка к пользователю
#         client, created = Client.objects.get_or_create(
#             email=client_email,
#             defaults={
#                 'user': user,
#                 'first_name': user.first_name,
#                 'last_name': user.last_name,
#                 'phone_number': client_phone,
#                 'chat_id': chat_id,
#             }
#         )

#         # Создание заказа на основе заявки
#         order = Order.objects.create(
#             service_request=service_request,
#             client=client,
#             service=service,
#             message=description,
#             status="pending"
#         )

#         # Отправка сообщения в Telegram
#         if chat_id:
#             bot.send_telegram_message(client.id, service_request.id, "Ваши данные для входа на сайт.", order.id)

#         return redirect(reverse('order_detail', args=[order.pk]))

#     return render(request, 'web/create_service_request.html', {'service': service})

def create_service_request(request, service_id):
    service = get_object_or_404(Service, pk=service_id)
    if request.method == 'POST':
        # Извлечение данных формы
        client_email = request.POST.get('client_email')
        client_phone = request.POST.get('client_phone')
        description = request.POST.get('description')
        chat_id = request.POST.get('client_chat_id')
        client_name = request.POST.get('client_name')

        # Проверка на наличие существующей заявки
        service_request = get_object_or_404(ServiceRequest, chat_id=chat_id)

        # Обновление данных заявки
        service_request.client_email = client_email
        service_request.client_phone = client_phone
        service_request.message = description
        service_request.save()

        # Создание клиента и пользователя, если необходимо
        user, _ = User.objects.get_or_create(
            username=f"{client_email.split('@')[0]}_{get_random_string(5)}",
            defaults={"email": client_email}
        )
        user.first_name = client_name.split()[0] if client_name else ""
        user.last_name = client_name.split()[-1] if len(client_name.split()) > 1 else ""
        user.save()

        client, _ = Client.objects.get_or_create(
            email=client_email,
            defaults={
                'user': user,
                'first_name': user.first_name,
                'last_name': user.last_name,
                'phone_number': client_phone,
                'chat_id': chat_id,
            }
        )

        # Создание заказа, связанного с заявкой
        order = Order.objects.create(
            service_request=service_request,
            client=client,
            service=service_request.service,
            message=description,
            status="pending"
        )

        # Отправка уведомления в Telegram
        bot.send_telegram_message(
            client.id,
            service_request.id,
            f"Ваш заказ на услугу '{service_request.service.name}' был успешно создан.",
            order.id
        )

        return redirect(reverse('order_detail', args=[order.pk]))

    return render(request, 'web/create_service_request.html', {'service': service})



def generate_qr_code(request, service_id):
    if request.method == 'POST':
        client_email = request.POST.get('client_email')
        client_phone = request.POST.get('client_phone')
        client_name = request.POST.get('client_name')

        # Создание или получение клиента
        user, _ = User.objects.get_or_create(
            username=f"{client_email.split('@')[0]}_{get_random_string(5)}",
            defaults={"email": client_email}
        )
        user.first_name = client_name.split()[0] if client_name else ""
        user.last_name = client_name.split()[-1] if len(client_name.split()) > 1 else ""
        user.save()

        client, _ = Client.objects.get_or_create(
            email=client_email,
            defaults={
                'user': user,
                'first_name': user.first_name,
                'last_name': user.last_name,
                'phone_number': client_phone
            }
        )

        # Создание новой заявки на услугу
        service = get_object_or_404(Service, pk=service_id)
        token = uuid.uuid4().hex

        service_request = ServiceRequest.objects.create(
            service=service,
            client=client,
            token=token
        )

        # Генерация ссылки для регистрации в Telegram
        telegram_settings = get_object_or_404(TelegramSettings, pk=1)
        registration_link = f'https://t.me/{telegram_settings.bot_name}?start=request_{service_request.id}_token_{urlsafe_base64_encode(force_bytes(token))}'

        # Генерация QR-кода
        qr = qrcode.make(registration_link)
        qr_code_dir = os.path.join(settings.STATICFILES_DIRS[0], 'qr_codes')
        qr_code_path = os.path.join(qr_code_dir, f"request_{service_request.id}.png")
        external_qr_link = f'static/qr_codes/request_{service_request.id}.png'

        if not os.path.exists(qr_code_dir):
            os.makedirs(qr_code_dir)

        qr.save(qr_code_path)

        return JsonResponse({
            'registration_link': registration_link,
            'qr_code_url': f"/{external_qr_link}",
            'service_request_id': service_request.id
        })
    else:
        return JsonResponse({'error': 'Метод запроса должен быть POST'}, status=405)

def complete_registration(request, request_id):
    # Завершение регистрации по идентификатору заявки
    service_request = get_object_or_404(ServiceRequest, pk=request_id)
    if request.method == 'POST':
        client_name = request.POST.get('client_name', service_request.client_name)
        client_email = request.POST.get('client_email', service_request.client_email)
        client_phone = request.POST.get('client_phone', service_request.client_phone)
        chat_id = request.POST.get('chat_id', service_request.chat_id)

        # Обновляем данные заявки
        service_request.client_name = client_name
        service_request.client_email = client_email
        service_request.client_phone = client_phone
        service_request.chat_id = chat_id
        service_request.save()

        return redirect('home')

    return render(request, 'web/complete_registration.html', {'service_request': service_request})
def request_status(request, service_id):
    # Проверяем статус заявки на услугу
    service_request = get_object_or_404(ServiceRequest, pk=service_id)
    is_verified = service_request.client_name != '' and service_request.chat_id != ''

    return JsonResponse({
        'is_verified': is_verified,
        'client_name': service_request.client_name,
        'client_chat_id' : service_request.chat_id,
})

def complete_registration_basic(request):
    # Базовая регистрация без идентификатора заявки
    if request.method == 'POST':
        client_name = request.POST.get('client_name')
        client_email = request.POST.get('client_email')
        client_phone = request.POST.get('client_phone')

        return redirect('home')

    return render(request, 'web/complete_registration_basic.html')

def check_service_request_data(request, token=None, request_id=None):
    # Проверка наличия данных в таблице ServiceRequest по токену или номеру заявки
    service_request = None
    if token:
        try:
            service_request = ServiceRequest.objects.get(token=token)
        except ServiceRequest.DoesNotExist:
            service_request = None
    elif request_id:
        try:
            service_request = ServiceRequest.objects.get(id=request_id)
        except ServiceRequest.DoesNotExist:
            service_request = None

    if service_request:
        return JsonResponse({
            'exists': True,
            'client_name': service_request.client_name,
            'client_email': service_request.client_email,
            'client_phone': service_request.client_phone,
            'chat_id': service_request.chat_id
        })
    else:
        return JsonResponse({'exists': False})

def order_detail(request, pk):
    order = get_object_or_404(Order, pk=pk)
    return render(request, 'web/order_detail.html', {'order': order})

@login_required
def client_orders(request):
    client = request.user.client_profile
    orders = client.related_orders.all()
    return render(request, 'web/client_orders.html', {'orders': orders})


def generate_secure_token(service_request_id, secret_key):
    """Генерация безопасного токена для подтверждения подлинности запроса."""
    data = f'{service_request_id}:{secret_key}'
    return hmac.new(secret_key.encode(), data.encode(), hashlib.sha256).hexdigest()

@csrf_exempt
def send_telegram_notification(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            service_request_id = data.get('service_request_id')
            provided_token = data.get('token')

            # Проверка корректности переданных данных
            if not service_request_id or not provided_token:
                return JsonResponse({'error': 'Недостаточно данных для подтверждения'}, status=400)

            # Получение заявки
            service_request = ServiceRequest.objects.filter(id=service_request_id).first()
            if not service_request:
                return JsonResponse({'error': 'Заявка не найдена'}, status=404)

            # Генерация токена и сравнение
            secret_key = settings.SECRET_KEY  # Используем секретный ключ из настроек
            expected_token = generate_secure_token(service_request_id, secret_key)

            if not hmac.compare_digest(provided_token, expected_token):
                return JsonResponse({'error': 'Неверный токен. Доступ запрещен.'}, status=403)

            # Отправка сообщения в Telegram
            chat_id = service_request.chat_id
            if not chat_id:
                return JsonResponse({'error': 'Нет chat_id для отправки сообщения'}, status=400)

            message = (
                f"Здравствуйте, {service_request.client_name}!\n"
                f"Ваша заявка на услугу '{service_request.service.name}' успешно зарегистрирована."
            )

            bot.send_telegram_message(chat_id=chat_id, message=message)

            return JsonResponse({'status': 'Уведомление успешно отправлено в Telegram'})

        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)

    return JsonResponse({'error': 'Метод запроса должен быть POST'}, status=405)