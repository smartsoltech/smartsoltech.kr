from django.db import models
from django.contrib.auth.models import AbstractUser, User
import uuid
from django.urls import reverse

class Category(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(default='Описание категории')

    class Meta:
        verbose_name = 'Категория'
        verbose_name_plural = 'Категории'
        ordering = ['name']

    def __str__(self):
        return self.name

class Service(models.Model):
    name = models.CharField(max_length=200)
    description = models.TextField(default='Описание услуги')
    price = models.DecimalField(max_digits=10, decimal_places=2)
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, related_name='services')
    image = models.ImageField(upload_to='static/img/services/', blank=True, null=True)

    class Meta:
        verbose_name = 'Услуга'
        verbose_name_plural = 'Услуги'
        ordering = ['name']

    def __str__(self):
        return self.name

    def average_rating(self):
        reviews = self.reviews.all()
        if reviews:
            return sum(review.rating for review in reviews) / reviews.count()
        return 0

    def review_count(self):
        return self.reviews.count()

class Client(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='client_profile', null=True, blank=True)
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    phone_number = models.CharField(max_length=15, unique=True)
    image = models.ImageField(upload_to='static/img/customer/', blank=True, null=True)
    chat_id = models.CharField(max_length=100, blank=True, null=True)  # Telegram chat ID

    class Meta:
        verbose_name = 'Клиент'
        verbose_name_plural = 'Клиенты'
        ordering = ['last_name', 'first_name']

    def __str__(self):
        return f"{self.first_name} {self.last_name} {self.chat_id}"

class BlogPost(models.Model):
    title = models.CharField(max_length=200)
    content = models.TextField()
    published_date = models.DateTimeField(auto_now_add=True)
    image = models.ImageField(upload_to='static/img/blog/', blank=True, null=True)

    class Meta:
        verbose_name = 'Блог'
        verbose_name_plural = 'Блоги'
        ordering = ['-published_date']

    def __str__(self):
        return self.title
    
class Order(models.Model):
    service = models.ForeignKey(Service, on_delete=models.CASCADE, related_name='related_orders')
    client = models.ForeignKey(Client, on_delete=models.CASCADE, related_name='related_orders')
    message = models.TextField(blank=True, null=True)
    order_date = models.DateTimeField(auto_now_add=True)
    status = models.CharField(
        max_length=50, 
        choices=[
            ('pending', 'Ожидание'), 
            ('in_progress', 'В процессе'), 
            ('completed', 'Завершен'), 
            ('cancelled', 'Отменён')
        ], 
        default='pending'
    )

    class Meta:
        ordering = ['-order_date']
        verbose_name = 'Заказ'
        verbose_name_plural = 'Заказы'

    def __str__(self):
        return f"Order #{self.id} by {self.client.first_name}"

    def is_completed(self):
        return self.status == 'completed'

    def get_absolute_url(self):
        return reverse('order_detail', kwargs={'pk': self.pk})

class Project(models.Model):
    name = models.CharField(max_length=200)
    description = models.TextField(default='Описание проекта')
    completion_date = models.DateField(blank=True, null=True)
    client = models.ForeignKey(Client, on_delete=models.CASCADE, related_name='projects')
    service = models.ForeignKey(Service, on_delete=models.CASCADE, related_name='projects')
    order = models.OneToOneField(Order, on_delete=models.CASCADE, related_name='project', null=True, blank=True)
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, blank=True)
    image = models.ImageField(upload_to='static/img/project/', blank=True, null=True)
    status = models.CharField(max_length=50, choices=[('in_progress', 'В процессе'), ('completed', 'Завершен')], default='in_progress')

    class Meta:
        verbose_name = 'Проект'
        verbose_name_plural = 'Проекты'
        ordering = ['-completion_date']

    def __str__(self):
        return self.name

class Review(models.Model):
    client = models.ForeignKey(Client, on_delete=models.CASCADE, related_name='reviews')
    service = models.ForeignKey(Service, on_delete=models.CASCADE, related_name='reviews')
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='reviews', blank=True, null=True)
    rating = models.IntegerField()
    comment = models.TextField()
    review_date = models.DateTimeField(auto_now_add=True)
    image = models.ImageField(upload_to='static/img/review/', blank=True, null=True)

    class Meta:
        verbose_name = 'Отзыв'
        verbose_name_plural = 'Отзывы'
        ordering = ['-review_date']

    def __str__(self):
        return f"Review by {self.client.first_name} {self.client.last_name} for {self.service.name}"

class ServiceRequest(models.Model):
    service = models.ForeignKey(Service, on_delete=models.CASCADE)
    client_name = models.CharField(max_length=100)
    client_email = models.EmailField()
    client_phone = models.CharField(max_length=20)
    created_at = models.DateTimeField(auto_now_add=True)
    token = models.UUIDField(default=uuid.uuid4, unique=True)  # Генерация уникального токена
    chat_id = models.CharField(max_length=100, blank=True, null=True)  # Telegram chat ID

    class Meta:
        verbose_name = 'Заявка на услугу'
        verbose_name_plural = 'Заявки на услуги'
        ordering = ['-created_at']

    def __str__(self):
        return f"Request for {self.service.name} by {self.client_name}"