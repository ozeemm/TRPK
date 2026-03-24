from rest_framework import serializers
from dental_clinic.models import *
from datetime import datetime, timedelta

class DoctorScheduleSerializer(serializers.ModelSerializer):
    reservation_date = serializers.DateField(format='%d.%m.%Y')
    reservation_time_start = serializers.TimeField(format='%H:%M')
    reservation_time_end = serializers.TimeField(format='%H:%M')
    is_reserved = serializers.SerializerMethodField()
    is_reservable = serializers.SerializerMethodField()

    class Meta:
        model = DoctorSchedule
        fields = '__all__'

    def get_is_reserved(self, obj):
        return obj.reservation_set.exists()

    def get_is_reservable(self, obj):
        now = datetime.now()
        slot_datetime = datetime.combine(obj.reservation_date, obj.reservation_time_start)
        time_left = slot_datetime - now
        return time_left > timedelta(hours=2)

class PatientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Patient
        fields = '__all__'

class DoctorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Doctor
        fields = '__all__'

class ReservationListSerializer(serializers.ModelSerializer):
    class DoctorScheludeWithDoctorSerializer(serializers.ModelSerializer):
        doctor = DoctorSerializer(read_only = True)
        class Meta:
            model = DoctorSchedule
            fields = '__all__'
    
    time_slot = DoctorScheludeWithDoctorSerializer(read_only=True)

    class Meta:
        model = Reservation
        fields = '__all__'

class ReservationCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Reservation
        fields = ['time_slot']

    def validate(self, data):
        patient = Patient.objects.filter(phone=self.context['request'].user.username).first()
        
        active_statuses = [
            Reservation.Status.RESERVED,
            Reservation.Status.AWAITING_CONFIRMATION,
            Reservation.Status.CONFIRMED
        ]

        active_count = Reservation.objects.filter(
            patient=patient,
            status__in=active_statuses
        ).count()

        if active_count >= 2:
            raise serializers.ValidationError("У вас уже есть 2 активные записи")
        
        return data

    def create(self, validated_data):
        patient = Patient.objects.filter(phone=self.context['request'].user.username).first()
        validated_data['patient'] = patient
        validated_data['status'] = Reservation.Status.RESERVED
        return super().create(validated_data)

class NotificationSerializer(serializers.ModelSerializer):
    message = serializers.SerializerMethodField()

    class Meta:
        model = Notification
        fields = ['id', 'reservation', 'sending_datetime', 'type', 'is_viewed', 'message']

    def get_message(self, obj):
        time_slot = obj.reservation.time_slot
        doctor = time_slot.doctor
        date = time_slot.reservation_date.strftime('%d.%m.%Y')
        time = time_slot.reservation_time_start.strftime('%H:%M')
        
        messages = {
            Notification.Type.RESERVED: f'Создана запись к врачу {doctor.surname} {doctor.name} {doctor.lastname} ({doctor.speciality}) на {date} в {time}',
            Notification.Type.AWAITING_CONFIRMATION: f'Пожалуйста, подтвердите запись к врачу {doctor.surname} {doctor.name} {doctor.lastname} ({doctor.speciality}) на {date} в {time}',
            Notification.Type.CONFIRMED: f'Запись к врачу {doctor.surname} {doctor.name} {doctor.lastname} ({doctor.speciality}) на {date} в {time} подтверждена',
            Notification.Type.CANCELLED: f'Запись к врачу {doctor.surname} {doctor.name} {doctor.lastname} ({doctor.speciality}) на {date} в {time} отменена',
        }
        return messages.get(obj.type, '')