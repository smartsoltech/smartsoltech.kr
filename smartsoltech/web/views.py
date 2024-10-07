from django.shortcuts import render, get_object_or_404, redirect
from .models import Service, Project, Client, BlogPost, Review, Order
from django.db.models import Avg


def home(request):
    return render(request, 'web/home.html')

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

# def create_order(request, pk):
#     if request.method == 'POST':
#         service = get_object_or_404(Service, pk=pk)
#         client_name = request.POST.get('client_name')
#         client_email = request.POST.get('client_email')
#         client_phone = request.POST.get('client_phone')
#         message = request.POST.get('message')

#         # Создаем клиента, если он не существует
#         client, created = Client.objects.get_or_create(
#             email=client_email,
#             defaults={'first_name': client_name, 'phone_number': client_phone}
#         )

#         # Создаем новый заказ
#         order = Order(
#             service=service,
#             client=client,
#             client_email=client.email,
#             client_phone=client.phone_number,
#             message=message,
#         )
#         order.save()

#         # Редирект на страницу подтверждения или обратно к услуге
#         return redirect('service_detail', pk=pk)



def create_order(request, pk):
    if request.method == 'POST':
        service = get_object_or_404(Service, pk=pk)
        client_name = request.POST.get('client_name')
        client_email = request.POST.get('client_email')
        client_phone = request.POST.get('client_phone')
        message = request.POST.get('message')

        # Создаем клиента, если он не существует
        client, created = Client.objects.get_or_create(
            email=client_email,
            defaults={'first_name': client_name, 'phone_number': client_phone}
        )

        # Создаем новый заказ
        order = Order(
            service=service,
            client=client,
            message=message,
        )
        order.save()

        # Редирект на страницу подтверждения или обратно к услуге
        return redirect('service_detail', pk=pk)
    
    
def about_view(request):
    return render(request, 'web/about.html')