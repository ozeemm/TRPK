from django.test import TestCase
from django.contrib.auth import get_user_model
from django.utils import timezone
from datetime import datetime, timedelta
from rest_framework.test import APIClient
from rest_framework import status
from dental_clinic.models import Patient, Doctor, DoctorSchedule, Reservation, Notification

User = get_user_model()

class ReservationConfirmationTests(TestCase):
    """Тесты для подтверждения записей"""

    def setUp(self):
        self.client = APIClient()
        
        # Создаём пользователя и пациента
        self.user = User.objects.create_user(
            username='+79991234567',
            password='testpass123'
        )
        self.patient = Patient.objects.create(
            surname='Иванов',
            name='Иван',
            lastname='Иванович',
            phone='+79991234567',
            birthday='2000-01-01',
            user=self.user
        )
        
        # Создаём врача
        self.doctor = Doctor.objects.create(
            surname='Петров',
            name='Пётр',
            lastname='Петрович',
            speciality='Терапевт'
        )
        
        # Создаём расписание на будущее
        self.schedule = DoctorSchedule.objects.create(
            doctor=self.doctor,
            reservation_date=timezone.now().date() + timedelta(days=2),
            reservation_time_start=datetime.strptime('10:00', '%H:%M').time(),
            reservation_time_end=datetime.strptime('11:00', '%H:%M').time()
        )
        
        # Создаём запись со статусом "Ожидает подтверждения"
        self.reservation = Reservation.objects.create(
            patient=self.patient,
            time_slot=self.schedule,
            status=Reservation.Status.AWAITING_CONFIRMATION
        )

    def test_confirm_reservation_success(self):
        """Успешное подтверждение записи"""
        self.client.force_login(self.user)
        
        response = self.client.post(
            f'/api/reservations/{self.reservation.id}/confirm/'
        )
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Проверяем, что статус изменился
        self.reservation.refresh_from_db()
        self.assertEqual(self.reservation.status, Reservation.Status.CONFIRMED)
        
        # Проверяем, что создано уведомление о подтверждении
        notification = Notification.objects.filter(
            reservation=self.reservation,
            type=Notification.Type.CONFIRMED
        ).first()
        self.assertIsNotNone(notification)

    def test_confirm_reservation_not_awaiting(self):
        """Попытка подтвердить запись, которая не ожидает подтверждения"""
        # Меняем статус на CONFIRMED
        self.reservation.status = Reservation.Status.CONFIRMED
        self.reservation.save()
        
        self.client.force_login(self.user)
        
        response = self.client.post(
            f'/api/reservations/{self.reservation.id}/confirm/'
        )
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('error', response.data)

    def test_confirm_reservation_reserved_status(self):
        """Попытка подтвердить запись со статусом RESERVED"""
        self.reservation.status = Reservation.Status.RESERVED
        self.reservation.save()
        
        self.client.force_login(self.user)
        
        response = self.client.post(
            f'/api/reservations/{self.reservation.id}/confirm/'
        )
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('error', response.data)

class ReservationCancellationTests(TestCase):
    """Тесты для отмены записей"""

    def setUp(self):
        self.client = APIClient()
        
        # Создаём пользователя и пациента
        self.user = User.objects.create_user(
            username='+79991234568',
            password='testpass123'
        )
        self.patient = Patient.objects.create(
            surname='Петров',
            name='Пётр',
            lastname='Петрович',
            phone='+79991234568',
            birthday='2000-01-01',
            user=self.user
        )
        
        # Создаём врача
        self.doctor = Doctor.objects.create(
            surname='Сидоров',
            name='Сидор',
            lastname='Сидорович',
            speciality='Хирург'
        )

    def test_cancel_reservation_reserved_status(self):
        """Успешная отмена записи со статусом RESERVED"""
        schedule = DoctorSchedule.objects.create(
            doctor=self.doctor,
            reservation_date=timezone.now().date() + timedelta(days=2),
            reservation_time_start=datetime.strptime('10:00', '%H:%M').time(),
            reservation_time_end=datetime.strptime('11:00', '%H:%M').time()
        )
        
        reservation = Reservation.objects.create(
            patient=self.patient,
            time_slot=schedule,
            status=Reservation.Status.RESERVED
        )
        
        self.client.force_login(self.user)
        
        response = self.client.post(
            f'/api/reservations/{reservation.id}/cancel/'
        )
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Проверяем, что статус изменился
        reservation.refresh_from_db()
        self.assertEqual(reservation.status, Reservation.Status.CANCELLED)
        
        # Проверяем, что создано уведомление об отмене
        notification = Notification.objects.filter(
            reservation=reservation,
            type=Notification.Type.CANCELLED
        ).first()
        self.assertIsNotNone(notification)

    def test_cancel_reservation_awaiting_confirmation_success(self):
        """Успешная отмена записи со статусом AWAITING_CONFIRMATION (более 3 часов)"""
        schedule = DoctorSchedule.objects.create(
            doctor=self.doctor,
            reservation_date=timezone.now().date() + timedelta(days=1),
            reservation_time_start=datetime.strptime('15:00', '%H:%M').time(),
            reservation_time_end=datetime.strptime('16:00', '%H:%M').time()
        )
        
        reservation = Reservation.objects.create(
            patient=self.patient,
            time_slot=schedule,
            status=Reservation.Status.AWAITING_CONFIRMATION
        )
        
        self.client.force_login(self.user)
        
        response = self.client.post(
            f'/api/reservations/{reservation.id}/cancel/'
        )
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        reservation.refresh_from_db()
        self.assertEqual(reservation.status, Reservation.Status.CANCELLED)

    def test_cancel_reservation_less_than_3_hours(self):
        """Отмена записи менее чем за 3 часа до приёма"""
        # Создаём запись на ближайшее время (менее 3 часов)
        schedule = DoctorSchedule.objects.create(
            doctor=self.doctor,
            reservation_date=timezone.now().date(),
            reservation_time_start=(timezone.now() + timedelta(hours=2)).time(),
            reservation_time_end=(timezone.now() + timedelta(hours=3)).time()
        )
        
        reservation = Reservation.objects.create(
            patient=self.patient,
            time_slot=schedule,
            status=Reservation.Status.AWAITING_CONFIRMATION
        )
        
        self.client.force_login(self.user)
        
        response = self.client.post(
            f'/api/reservations/{reservation.id}/cancel/'
        )
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('error', response.data)
        self.assertIn('менее 3-х часов', response.data['error'])
        
        # Проверяем, что статус не изменился
        reservation.refresh_from_db()
        self.assertEqual(reservation.status, Reservation.Status.AWAITING_CONFIRMATION)

    def test_cancel_reservation_already_confirmed(self):
        """Попытка отмены уже подтверждённой записи"""
        schedule = DoctorSchedule.objects.create(
            doctor=self.doctor,
            reservation_date=timezone.now().date() + timedelta(days=2),
            reservation_time_start=datetime.strptime('10:00', '%H:%M').time(),
            reservation_time_end=datetime.strptime('11:00', '%H:%M').time()
        )
        
        reservation = Reservation.objects.create(
            patient=self.patient,
            time_slot=schedule,
            status=Reservation.Status.CONFIRMED
        )
        
        self.client.force_login(self.user)
        
        response = self.client.post(
            f'/api/reservations/{reservation.id}/cancel/'
        )
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('error', response.data)
        
        # Проверяем, что статус не изменился
        reservation.refresh_from_db()
        self.assertEqual(reservation.status, Reservation.Status.CONFIRMED)

    def test_cancel_reservation_already_cancelled(self):
        """Попытка отмены уже отменённой записи"""
        schedule = DoctorSchedule.objects.create(
            doctor=self.doctor,
            reservation_date=timezone.now().date() + timedelta(days=2),
            reservation_time_start=datetime.strptime('10:00', '%H:%M').time(),
            reservation_time_end=datetime.strptime('11:00', '%H:%M').time()
        )
        
        reservation = Reservation.objects.create(
            patient=self.patient,
            time_slot=schedule,
            status=Reservation.Status.CANCELLED
        )
        
        self.client.force_login(self.user)
        
        response = self.client.post(
            f'/api/reservations/{reservation.id}/cancel/'
        )
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('error', response.data)