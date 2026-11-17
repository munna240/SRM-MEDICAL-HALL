from django.urls import path
from . import views

urlpatterns = [
    path('login/', views.login_view, name='login'),
    path('dashboard/', views.dashboard_view, name='dashboard'),
    path('logout/', views.logout_view, name='logout'),

    path('register/staff/', views.staff_register, name='staff_register'),
    path('register/doctor/', views.doctor_register, name='doctor_register'),

    # Doctor Profile
    path('doctor/profile/', views.doctor_profile, name='doctor_profile'),
    path('doctor/profile/edit/', views.doctor_profile_edit, name='doctor_profile_edit'),

    # Doctor Patients
    path('doctor/patients/', views.doctor_patients, name='doctor_patients'),
    path(
        'doctor/patients/<str:patient_id>/',
        views.doctor_patient_detail,
        name='doctor_patient_detail'
    ),
    path(
    'doctor/patients/<str:patient_id>/prescription/create/',
    views.doctor_create_prescription,
    name='doctor_create_prescription'
),
path(
        'doctor/prescription/new-patient/',
        views.doctor_new_patient_prescription,
        name='doctor_new_patient_prescription'
    ),
]