from django.contrib import admin
from .models import Service, Project, Client, Order, Review, BlogPost, Category

@admin.register(Service)
class ServiceAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'price')
    search_fields = ('name', 'category')

@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = ('name','category', 'client')
    list_filter = ('category',)
    search_fields = ('name', 'client__first_name', 'client__last_name')

@admin.register(Client)
class ClientAdmin(admin.ModelAdmin):
    list_display = ('first_name', 'last_name', 'email', 'phone_number')
    search_fields = ('first_name', 'last_name', 'email')

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('client', 'order_date', 'client_email', 'client_phone', 'service', 'order_date', 'status')
    list_filter = ('status','client', 'order_date')
    search_fields = ('client__first_name', 'service__name','status','client', 'order_date')

@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ('client', 'service', 'rating', 'review_date')
    list_filter = ('rating',)
    search_fields = ('client__first_name', 'service__name')

@admin.register(BlogPost)
class BlogPostAdmin(admin.ModelAdmin):
    list_display = ('title', 'published_date')
    search_fields = ('title',)
    
@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name','description')
    search_fields = ('name',)
    
