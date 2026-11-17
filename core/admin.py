
from django.contrib import admin
from .models import Patient, Prescription, PrescriptionMedicine


@admin.register(Patient)
class PatientAdmin(admin.ModelAdmin):

    list_display = (
        'patient_id',
        'full_name',
        'phone',
        'gender',
        'blood_group',
        'assigned_doctor',
        'created_at',
    )

    search_fields = (
        'patient_id',
        'full_name',
        'phone',
    )

    list_filter = (
        'gender',
        'blood_group',
        'is_active',
    )

    readonly_fields = (
        'patient_id',
        'created_at',
        'updated_at',
    )


class PrescriptionMedicineInline(admin.TabularInline):
    model = PrescriptionMedicine
    extra = 1


@admin.register(Prescription)
class PrescriptionAdmin(admin.ModelAdmin):

    list_display = (
        'prescription_id',
        'patient',
        'doctor',
        'status',
        'created_at',
    )

    search_fields = (
        'prescription_id',
        'patient__full_name',
        'patient__patient_id',
        'doctor__username',
    )

    list_filter = (
        'status',
        'created_at',
    )

    readonly_fields = (
        'prescription_id',
        'created_at',
        'updated_at',
        'finalized_at',
    )

    inlines = [PrescriptionMedicineInline]


@admin.register(PrescriptionMedicine)
class PrescriptionMedicineAdmin(admin.ModelAdmin):

    list_display = (
        'medicine_name',
        'prescription',
        'dosage',
        'frequency',
        'duration',
    )

    search_fields = (
        'medicine_name',
        'prescription__prescription_id',
    )
