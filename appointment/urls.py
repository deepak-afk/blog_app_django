from django.urls import path
from . import views

app_name = 'appointment'

urlpatterns = [
    path('doctors/', views.doctor_list, name='doctor_list'),
    path('book-appointment/<int:doctor_id>/', views.book_appointment, name='book_appointment'),
    path('add_doctor/', views.add_doctor, name='add_doctor'),
    path('appointments-patients/', views.patient_appointments, name='patient_appointments'),
    path('appointments-doctors/', views.doctor_appointments, name='doctor_appointments'),
]