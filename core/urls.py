
from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),

    # Patient Management
    path('patients/', views.patient_list, name='patient_list'),
    path('patients/register/', views.patient_register, name='patient_register'),

    path(
        'patients/<str:patient_id>/edit/',
        views.patient_edit,
        name='patient_edit'
    ),

    path(
        'patients/<str:patient_id>/',
        views.patient_detail,
        name='patient_detail'
    ),

    # Prescription Directory
    path(
        'prescriptions/',
        views.prescription_list,
        name='prescription_list'
    ),

    # Deleted Prescriptions
    path(
        'prescriptions/deleted/',
        views.deleted_prescription_list,
        name='deleted_prescription_list'
    ),

    # Prescription Restore
    path(
        'prescriptions/<str:prescription_id>/restore/',
        views.prescription_restore,
        name='prescription_restore'
    ),

    # Prescription Edit
    path(
        'prescriptions/<str:prescription_id>/edit/',
        views.prescription_edit,
        name='prescription_edit'
    ),

    # Prescription Delete
    path(
        'prescriptions/<str:prescription_id>/delete/',
        views.prescription_delete,
        name='prescription_delete'
    ),

    # Prescription Version History
    path(
        'prescriptions/<str:prescription_id>/history/',
        views.prescription_history,
        name='prescription_history'
    ),

    # QR Code Online Verification
    path(
        'verify-prescription/<uuid:token>/',
        views.verify_prescription,
        name='verify_prescription'
    ),

    # Prescription Details
    path(
        'prescriptions/<str:prescription_id>/',
        views.prescription_detail,
        name='prescription_detail'
    ),
]
