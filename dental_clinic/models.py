from django.db import models

# Пациент
class Patient(models.Model):
    surname = models.TextField("Фамилия")
    name = models.TextField("Имя")
    lastname = models.TextField("Отчество")
    phone = models.TextField("Номер телефона")
    birthday = models.DateField("День рождения")
    user = models.ForeignKey("auth.User", verbose_name="Пользователь", on_delete=models.CASCADE, null=False)

    class Meta:
        verbose_name = 'Пациент'
        verbose_name_plural = 'Пациенты'

    def __str__(self):
        return f"{self.surname} {self.name} {self.lastname}"
    
# Врач
class Doctor(models.Model):
    surname = models.TextField("Фамилия")
    name = models.TextField("Имя")
    lastname = models.TextField("Отчество")
    speciality = models.TextField("Специальность")

    class Meta:
        verbose_name = 'Врач'
        verbose_name_plural = 'Врачи'
    
    def __str__(self):
        return f"{self.surname} {self.name} {self.lastname} ({self.speciality})"

# Расписание врача
class DoctorSchedule(models.Model):
    doctor = models.ForeignKey("Doctor", verbose_name="Врач", on_delete=models.CASCADE, null=False)
    reservation_date = models.DateField("Дата приёма")
    reservation_time_start = models.TimeField("Начало временного слота")
    reservation_time_end = models.TimeField("Конец временного слота")

    class Meta:
        verbose_name = 'Расписание врача'
        verbose_name_plural = 'Расписания врачей'
    
    def __str__(self):
        return f"{str(self.reservation_date)} {str(self.reservation_time_start)}-{str(self.reservation_time_end)}"

# Запись к врачу
class Reservation(models.Model):
    class Status(models.TextChoices):
        RESERVED = "Reserved", "Забронирована"
        AWAITING_CONFIRMATION = "Awaiting Confirmation", "Ожидает подтверждения"
        CONFIRMED = "Confirmed", "Подтверждена"
        CANCELLED = "Cancelled", "Отменена"
        COMPLETED = "Completed", "Завершена"

    patient = models.ForeignKey("Patient", verbose_name='Пациент', on_delete=models.CASCADE, null=False)
    time_slot = models.ForeignKey("DoctorSchedule", verbose_name='Временной слот', on_delete=models.CASCADE, null=False)
    status = models.TextField("Статус", choices=Status.choices)

    class Meta:
        verbose_name = 'Запись к врачу'
        verbose_name_plural = 'Записи к врачам'

# Уведомление
class Notification(models.Model):
    class Type(models.TextChoices):
        RESERVED = "Reserved", "Уведомление о создании записи"
        AWAITING_CONFIRMATION = "Awaiting Confirmation", "Уведомление о необходимости подтверждения записи"
        CONFIRMED = "Confirmed", "Уведомление о подтверждении записи"
        CANCELLED = "Cancelled", "Уведомление об отмене записи"

    reservation = models.ForeignKey("Reservation", verbose_name='Запись', on_delete=models.CASCADE, null=False)
    sending_datetime = models.DateTimeField("Дата и время отправки")
    type = models.TextField("Тип", choices=Type.choices)
    is_viewed = models.BooleanField("Просмотрено", default=False)

    class Meta:
        verbose_name = 'Уведомление'
        verbose_name_plural = 'Уведомления'