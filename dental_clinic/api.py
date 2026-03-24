from rest_framework.viewsets import GenericViewSet
from rest_framework import mixins, status
from rest_framework import serializers
from rest_framework.decorators import action
from rest_framework.response import Response
from django.contrib.auth import authenticate, login, logout
from datetime import timedelta
from dental_clinic.models import *
from dental_clinic.serializers import *
from dental_clinic.services import *

class UserProfileViewset(GenericViewSet):
    serializer_class = None
    
    class LoginSerializer(serializers.Serializer):
        phone = serializers.CharField()
        password = serializers.CharField()

    @action(url_path="login", detail=False, methods=["POST"])
    def login(self, request, *args, **kwargs):
        serializer = self.LoginSerializer(data=request.data)

        if(not serializer.is_valid()):
            return Response(status=status.HTTP_400_BAD_REQUEST)

        userdata = serializer.validated_data
        user = authenticate(username = userdata['phone'], password = userdata['password'])

        if(user is not None):
            login(request, user)
            return Response(status=status.HTTP_200_OK)
        else:
            return Response(status=status.HTTP_401_UNAUTHORIZED)

    @action(url_path="logout", detail=False, methods=["POST"])
    def logout(self, request, *args, **kwargs):
        logout(request)
        return Response(status=status.HTTP_200_OK)

    @action(url_name="info", detail=False, methods=["GET"])
    def info(self, request, *args, **kwargs):
        user = request.user
        data = { "is_authenticated": user.is_authenticated }

        if user.is_authenticated:
            patient = Patient.objects.filter(phone=user.username).first()
            data.update({
                "surname": patient.surname,
                "name": patient.name,
                "lastname": patient.lastname,
                "phone": patient.phone,
                "birthday": patient.birthday,
            })

        return Response(data)

class DoctorViewset(mixins.ListModelMixin, GenericViewSet):
    queryset = Doctor.objects.all()
    serializer_class = DoctorSerializer

    def list(self, request, *args, **kwargs):
        doctors = self.get_queryset()
        serializer = self.get_serializer(doctors, many=True)
        
        data = {}
        for doctor_data in serializer.data:
            speciality = doctor_data["speciality"]
            if speciality not in data:
                data[speciality] = []
    
            data[speciality].append(doctor_data)    
        return Response(data)

class DoctorScheduleViewset(mixins.RetrieveModelMixin, GenericViewSet):
    queryset = DoctorSchedule.objects.all()
    serializer_class = DoctorScheduleSerializer

    def retrieve(self, request, *args, **kwargs):
        doctor_id = kwargs.get('pk')
        
        today = datetime.now().date()
        start_of_current_week = today - timedelta(days=today.weekday())
        end_of_next_week = start_of_current_week + timedelta(weeks=2) - timedelta(days=1)
        
        schedules = self.get_queryset().filter(
            doctor_id=doctor_id,
            reservation_date__gte=start_of_current_week,
            reservation_date__lte=end_of_next_week
        ).order_by('reservation_date', 'reservation_time_start')
        
        serializer = self.get_serializer(schedules, many=True)

        return Response(serializer.data)

class ReservationViewset(mixins.ListModelMixin, mixins.CreateModelMixin, GenericViewSet):
    queryset = Reservation.objects.all()

    def get_queryset(self):
        qs = super().get_queryset()

        patient_phone = Patient.objects.filter(phone=self.request.user.username).first()
        if patient_phone:
            qs = qs.filter(patient=patient_phone).order_by('time_slot__reservation_date', 'time_slot__reservation_time_start')
        else:
            qs = Reservation.objects.none()
        return qs

    def get_serializer_class(self):
        if self.action == 'list':
            return ReservationListSerializer
        elif self.action == 'create':
            return ReservationCreateSerializer
        
    def list(self, request, *args, **kwargs):        
        self.change_upcoming_reservation_statuses()
        
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        reservations = serializer.data

        data = {}
        data["Confirmation"] = []
        data["Reserved"] = []
        data["Past"] = []

        for reservation in reservations:
            status = reservation["status"]

            if status == Reservation.Status.CONFIRMED or status == Reservation.Status.AWAITING_CONFIRMATION:
                data["Confirmation"].append(reservation)
            if status == Reservation.Status.RESERVED:
                data["Reserved"].append(reservation)
            if status == Reservation.Status.CANCELLED or status == Reservation.Status.COMPLETED:
                data["Past"].append(reservation)

        return Response(data)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        reservation = serializer.save()
        NotificationService.create_reservation_notification(reservation)

        return Response(serializer.data)

    def change_upcoming_reservation_statuses(self):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)

        now = datetime.now()

        for reservation_data in serializer.data:
            if(reservation_data.get('status') != Reservation.Status.RESERVED):
                continue

            time_slot = reservation_data.get("time_slot")
            if not time_slot:
                continue

            reservation_date = time_slot.get("reservation_date")
            reservation_time_start = time_slot.get("reservation_time_start")

            if not reservation_date or not reservation_time_start:
                continue

            slot_datetime = datetime.strptime(f"{reservation_date} {reservation_time_start}", "%Y-%m-%d %H:%M:%S")

            time_left = slot_datetime - now
            if timedelta(0) < time_left < timedelta(days=1):
                reservation_obj = Reservation.objects.get(id=reservation_data["id"])
                reservation_obj.status = Reservation.Status.AWAITING_CONFIRMATION
                reservation_obj.save()
                NotificationService.awaiting_confirmation_notification(reservation_obj)

    @action(url_path='confirm', detail=True, methods=['POST'])
    def confirm_reservation(self, request, pk=None):
        reservation = Reservation.objects.get(pk=pk)

        if reservation.status != Reservation.Status.AWAITING_CONFIRMATION:
            return Response(
                {"error": "Запись не ожидает подтверждения"},
                status=status.HTTP_400_BAD_REQUEST
            )

        reservation.status = Reservation.Status.CONFIRMED
        reservation.save()

        NotificationService.confirm_reservation_notification(reservation)

        return Response(status=status.HTTP_200_OK)
    
    @action(url_path='cancel', detail=True, methods=['GET'])
    def cancel_reservation(self, request, pk=None):
        reservation = Reservation.objects.get(pk=pk)

        if reservation.status not in [Reservation.Status.RESERVED, Reservation.Status.AWAITING_CONFIRMATION]:
            return Response(
                {"error": "Запись не может быть отменена"},
                status=status.HTTP_400_BAD_REQUEST
            )

        if reservation.status == Reservation.Status.AWAITING_CONFIRMATION:
            time_slot = reservation.time_slot
            slot_datetime = datetime.combine(time_slot.reservation_date, time_slot.reservation_time_start)
            time_left = slot_datetime - datetime.now()
            
            if time_left <= timedelta(hours=3):
                return Response(
                    {"error": "Запись не может быть отменена, так как до начала приёма осталось менее 3-х часов. Для отмены свяжитесь с администратором клиники"},
                    status=status.HTTP_400_BAD_REQUEST
                )

        reservation.status = Reservation.Status.CANCELLED
        reservation.save()

        NotificationService.cancel_reservation_notification(reservation)

        return Response(status=status.HTTP_200_OK)

class NotificationViewset(mixins.ListModelMixin, GenericViewSet):
    queryset = Notification.objects.all()

    def get_serializer_class(self):
        return NotificationSerializer

    def get_queryset(self):
        qs = super().get_queryset()

        patient = Patient.objects.filter(phone=self.request.user.username).first()
        if patient:
            qs = qs.filter(reservation__patient=patient).order_by('-sending_datetime')
        else:
            qs = Notification.objects.none()
        return qs

    @action(url_path='read', detail=False, methods=['POST'])
    def read(self, request, pk=None):
        patient = Patient.objects.filter(phone=request.user.username).first()
        if not patient:
            return Response(
                {"error": "Пользователь не найден"},
                status=status.HTTP_404_NOT_FOUND
            )

        notification_ids = request.data.get('notifications', [])
        if not notification_ids:
            return Response(
                {"error": "Не передан список идентификаторов уведомлений"},
                status=status.HTTP_400_BAD_REQUEST
            )

        updated_count = Notification.objects.filter(
            id__in=notification_ids,
            reservation__patient=patient
        ).update(is_viewed=True)

        return Response({"updated": updated_count}, status=status.HTTP_200_OK)