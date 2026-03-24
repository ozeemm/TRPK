from django.core.management.base import BaseCommand
from dental_clinic.models import Reservation, Notification

class Command(BaseCommand):
    def handle(self, *args, **kwargs):
        Notification.objects.all().delete()
        Reservation.objects.all().delete()
        print("Записи и уведомления удалены")