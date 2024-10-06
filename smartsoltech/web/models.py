# web/models.py
from django.db import models

class Category(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField()
    def __str__(self):
        return self.name

class Service(models.Model):
    name = models.CharField(max_length=200)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, related_name='services')
    image = models.ImageField(upload_to='static/img/services/', blank=True, null=True)

    def __str__(self):
        return self.name

    def average_rating(self):
        reviews = self.reviews.all()
        if reviews:
            return sum(review.rating for review in reviews) / reviews.count()
        return 0

    def review_count(self):
        return self.reviews.count()
class Project(models.Model):
    name = models.CharField(max_length=200)
    description = models.TextField()
    completion_date = models.DateField()
    client = models.ForeignKey('Client', on_delete=models.CASCADE, related_name='projects')
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, related_name='projects')
    image = models.ImageField(upload_to='static/img/project/', blank=True, null=True)

    def __str__(self):
        return self.name

class Review(models.Model):
    client = models.ForeignKey('Client', on_delete=models.CASCADE, related_name='reviews')
    service = models.ForeignKey('Service', on_delete=models.CASCADE, related_name='reviews', null=True, blank=True)
    project = models.ForeignKey('Project', on_delete=models.CASCADE, related_name='reviews', null=True, blank=True)
    rating = models.IntegerField()
    comment = models.TextField()
    review_date = models.DateTimeField(auto_now_add=True)
    image = models.ImageField(upload_to='static/img/review/', blank=True, null=True)

    def __str__(self):
        if self.service:
            return f"Review by {self.client} for service: {self.service}"
        elif self.project:
            return f"Review by {self.client} for project: {self.project}"
        else:
            return f"Review by {self.client}"

class Client(models.Model):
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    email = models.EmailField()
    phone_number = models.CharField(max_length=15)
    image = models.ImageField(upload_to='static/img/customer/', blank=True, null=True)

    def __str__(self):
        return f"{self.first_name} {self.last_name}"

class Order(models.Model):
    service = models.ForeignKey(Service, on_delete=models.CASCADE, related_name='orders')
    client = models.ForeignKey(Client, on_delete=models.CASCADE, related_name='orders')
    client_email = models.EmailField(default='notprovided@example.com')
    client_phone = models.CharField(max_length=15, default='unknown')
    message = models.TextField(blank=True, null=True)
    order_date = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=50, choices=[('pending', 'Pending'), ('completed', 'Completed'), ('cancelled', 'Cancelled')], default='pending')

    def __str__(self):
        return f"Order #{self.id} by {self.client.first_name} {self.client.last_name}"



class BlogPost(models.Model):
    title = models.CharField(max_length=200)
    content = models.TextField()
    published_date = models.DateTimeField(auto_now_add=True)
    image = models.ImageField(upload_to='static/img/blog/', blank=True, null=True)

    def __str__(self):
        return self.title