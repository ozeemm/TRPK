from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from dental_clinic.models import Patient, Doctor, DoctorSchedule, Reservation, Notification
from datetime import datetime, time
from calendar import monthrange

class Command(BaseCommand):
    def handle(self, *args, **kwargs):
        print("Удаление данных")
        self.clear_data()

        self.generate_doctors_and_schedule()
        print(f"Создано {Doctor.objects.count()} врачей")
        print(f"Создано {DoctorSchedule.objects.count()} слотов для записи")

        self.generate_patients()
        print(f"Создано {Patient.objects.count()} пациентов")

    def clear_data(self):
        Notification.objects.all().delete()
        Reservation.objects.all().delete()
        DoctorSchedule.objects.all().delete()
        Doctor.objects.all().delete()
        Patient.objects.all().delete()
    
    def generate_doctors_and_schedule(self):
        doctors_data = [
            {
                "surname": "Иванов", 
                "name": "Иван", 
                "lastname": "Иванович", 
                "speciality": "Терапевт",
                "work_days": [0, 1, 3], # Понедельник, вторник, четверг
                "time_slots":  [
                    (time(10, 0), time(11, 0)),
                    (time(11, 0), time(12, 0)),
                    (time(12, 0), time(13, 0)),
                    (time(14, 0), time(15, 0)),
                    (time(15, 0), time(16, 0)),
                ]
            },
            {
                "surname": "Петров", 
                "name": "Пётр", 
                "lastname": "Петрович", 
                "speciality": "Хирург",
                "work_days": [1, 4], # Вторник, пятница
                "time_slots": [
                    (time(10, 0), time(11, 0)),
                    (time(11, 0), time(13, 0)),
                    (time(14, 0), time(16, 0)),
                    (time(16, 0), time(17, 0)),
                ]
            },
            {
                "surname": "Сидоров", 
                "name": "Сергей", 
                "lastname": "Сергеевич", 
                "speciality": "Ортодонт",
                "work_days": [2, 3], # Среда, четверг
                "time_slots": [
                    (time(10, 0), time(11, 0)),
                    (time(11, 0), time(13, 0)),
                    (time(14, 0), time(16, 0)),
                    (time(16, 0), time(17, 0)),
                ]
            },
            {
                "surname": "Кузнецова", 
                "name": "Елена", "lastname": 
                "Дмитриевна", 
                "speciality": "Детский стоматолог",
                "work_days": [0, 1, 4], # Понедельник, вторник, пятница
                "time_slots": [
                    (time(10, 0), time(11, 0)),
                    (time(11, 0), time(12, 0)),
                    (time(12, 0), time(13, 0)),
                    (time(14, 0), time(15, 0)),
                    (time(15, 0), time(16, 0)),
                ]
            },
            {
                "surname": "Попов", 
                "name": "Алексей", 
                "lastname": "Николаевич", 
                "speciality": "Терапевт",
                "work_days": [2, 3, 4], # Среда, четверг, пятница
                "time_slots": [
                    (time(10, 0), time(11, 0)),
                    (time(11, 0), time(12, 0)),
                    (time(12, 0), time(13, 0)),
                    (time(14, 0), time(15, 0)),
                    (time(15, 0), time(16, 0)),
                ]
            },
        ]

        today = datetime.now().date()

        for doctor_data in doctors_data:
            doctor = Doctor.objects.create(
                surname=doctor_data["surname"],
                name=doctor_data["name"],
                lastname=doctor_data["lastname"],
                speciality=doctor_data["speciality"]
            )

            for month_offset in range(2):
                year = today.year
                month = today.month + month_offset
                if month > 12:
                    month -= 12
                    year += 1

                days_in_month = monthrange(year, month)[1]

                for day in range(1, days_in_month + 1):
                    current_date = datetime(year, month, day).date()

                    if current_date.weekday() not in doctor_data["work_days"]:
                        continue

                    for time_start, time_end in doctor_data["time_slots"]:
                        DoctorSchedule.objects.create(
                            doctor=doctor,
                            reservation_date=current_date,
                            reservation_time_start=time_start,
                            reservation_time_end=time_end
                        )

    def generate_patients(self):
        
        patients_data = [
            {
                "surname": "Смирнов",
                "name": "Александр",
                "lastname": "Александрович",
                "phone": "80000000001",
                "birthday": datetime(1990, 5, 15).date(),
            },
            {
                "surname": "Новиков",
                "name": "Дмитрий",
                "lastname": "Владимирович",
                "phone": "80000000002",
                "birthday": datetime(1995, 12, 3).date(),
            },
            {
                "surname": "Козлова",
                "name": "Мария",
                "lastname": "Сергеевна",
                "phone": "80000000003",
                "birthday": datetime(1985, 8, 22).date(),
            }
        ]

        for patient_data in patients_data:
            user = User.objects.create_user(
                username=patient_data["phone"],
                password="123"
            )
            Patient.objects.create(
                surname=patient_data["surname"],
                name=patient_data["name"],
                lastname=patient_data["lastname"],
                phone=patient_data["phone"],
                birthday=patient_data["birthday"],
                user=user
            )