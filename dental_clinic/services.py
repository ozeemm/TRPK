from datetime import datetime
from dental_clinic.models import Notification, Reservation

class NotificationService:
    @staticmethod
    def create_reservation_notification(reservation: Reservation):
        NotificationService.create_notification(reservation, Notification.Type.RESERVED)

    @staticmethod
    def awaiting_confirmation_notification(reservation: Reservation):
        NotificationService.create_notification(reservation, Notification.Type.AWAITING_CONFIRMATION)

    @staticmethod
    def confirm_reservation_notification(reservation: Reservation):
        NotificationService.create_notification(reservation, Notification.Type.CONFIRMED)

    @staticmethod
    def cancel_reservation_notification(reservation: Reservation):
        NotificationService.create_notification(reservation, Notification.Type.CANCELLED)

    @staticmethod
    def create_notification(reservation: Reservation, type):
        notification = Notification(
            reservation=reservation,
            sending_datetime=datetime.now(),
            type=type,
            is_viewed=False
        )
        notification.save()