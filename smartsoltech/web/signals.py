from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Order, Project

@receiver(post_save, sender=Order)
def create_project_on_order_completed(sender, instance, **kwargs):
    if instance.status == 'completed' and not Project.objects.filter(order=instance).exists():
        Project.objects.create(
            name=f"Project for {instance.service.name}",
            description=instance.message,
            client=instance.client,
            service=instance.service,
            order=instance,
            category=instance.service.category,
            status='in_progress'
        )

@receiver(post_save, sender=Project)
def prompt_review_on_project_completion(sender, instance, **kwargs):
    if instance.status == 'completed':
        # Logic to prompt the client for a review (e.g., sending an email or notification)
        pass
