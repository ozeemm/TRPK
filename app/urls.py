from django.contrib import admin
from django.urls import path
from django.conf.urls import include
from rest_framework.routers import DefaultRouter
from dental_clinic.api import *

router = DefaultRouter()
router.register("user", UserProfileViewset, basename="user")
router.register("doctors", DoctorViewset, basename="doctors")
router.register("doctorschedule", DoctorScheduleViewset, basename="doctorschedule")
router.register("reservations", ReservationViewset, basename="reservations")
router.register("notifications", NotificationViewset, basename="notifications")

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include(router.urls))
]
