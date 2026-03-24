from django.contrib import admin
from dental_clinic.models import Patient, Doctor, DoctorSchedule, Reservation, Notification

@admin.register(Patient)
class PatientAdmin(admin.ModelAdmin):
    list_display = ['id', 'surname', 'name', 'lastname', 'phone', 'birthday', 'user']

@admin.register(Doctor)
class DoctorAdmin(admin.ModelAdmin):
    list_display = ['id', 'surname', 'name', 'lastname', 'speciality']

@admin.register(DoctorSchedule)
class DoctorScheduleAdmin(admin.ModelAdmin):
    list_display = ['id', 'doctor', 'reservation_date', 'get_time_start', 'get_time_end']

    def get_time_start(self, obj):
        return obj.reservation_time_start.strftime('%H:%M')
    get_time_start.short_description = 'Начало'

    def get_time_end(self, obj):
        return obj.reservation_time_end.strftime('%H:%M')
    get_time_end.short_description = 'Конец'

@admin.register(Reservation)
class ReservationAdmin(admin.ModelAdmin):
    list_display = ['id', 'patient', 'time_slot', 'status']

@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ['id', 'reservation', 'sending_datetime', 'type', 'is_viewed']