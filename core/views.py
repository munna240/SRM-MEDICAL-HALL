
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User

from accounts.decorators import role_required
from .models import (
    Patient,
    Prescription,
    PrescriptionMedicine,
    PrescriptionVersion
)
from django.db import transaction
from django.utils import timezone
import base64
from .qr_utils import generate_prescription_qr

def home(request):
    return render(request, 'core/home.html')


# =========================
# PATIENT REGISTRATION
# =========================

@login_required
@role_required('ADMIN', 'STAFF')
def patient_register(request):

    doctors = User.objects.filter(
        profile__role='DOCTOR',
        profile__status='APPROVED'
    ).order_by('first_name')

    if request.method == 'POST':

        full_name = request.POST.get('full_name', '').strip()
        phone = request.POST.get('phone', '').strip()
        date_of_birth = request.POST.get('date_of_birth') or None
        gender = request.POST.get('gender')
        blood_group = request.POST.get('blood_group', 'UNKNOWN')
        address = request.POST.get('address', '').strip()
        allergies = request.POST.get('allergies', '').strip()
        medical_history = request.POST.get('medical_history', '').strip()
        doctor_id = request.POST.get('assigned_doctor')

        if not all([full_name, phone, gender]):
            messages.error(request, 'Please fill in all required fields.')

        elif gender not in dict(Patient.GENDER_CHOICES):
            messages.error(request, 'Invalid gender selection.')

        elif blood_group not in dict(Patient.BLOOD_GROUP_CHOICES):
            messages.error(request, 'Invalid blood group selection.')

        else:

            assigned_doctor = None

            if doctor_id:
                assigned_doctor = doctors.filter(id=doctor_id).first()

                if not assigned_doctor:
                    messages.error(request, 'Selected doctor is not available.')
                    return render(
                        request,
                        'core/patient_register.html',
                        {'doctors': doctors}
                    )

            Patient.objects.create(
                full_name=full_name,
                phone=phone,
                date_of_birth=date_of_birth,
                gender=gender,
                blood_group=blood_group,
                address=address,
                allergies=allergies,
                medical_history=medical_history,
                assigned_doctor=assigned_doctor,
                created_by=request.user
            )

            messages.success(request, 'Patient registered successfully.')
            return redirect('patient_list')

    return render(
        request,
        'core/patient_register.html',
        {'doctors': doctors}
    )


# =========================
# PATIENT LIST
# =========================

@login_required
@role_required('ADMIN', 'STAFF')
def patient_list(request):

    patients = Patient.objects.filter(
        is_active=True
    ).select_related(
        'assigned_doctor',
        'created_by'
    ).order_by('-created_at')

    return render(
        request,
        'core/patient_list.html',
        {'patients': patients}
    )


# =========================
# PATIENT DETAILS
# =========================

@login_required
@role_required('ADMIN', 'STAFF')
def patient_detail(request, patient_id):

    patient = get_object_or_404(
        Patient,
        patient_id=patient_id,
        is_active=True
    )

    return render(
        request,
        'core/patient_detail.html',
        {'patient': patient}
    )


# =========================
# EDIT PATIENT
# =========================

@login_required
@role_required('ADMIN', 'STAFF')
def patient_edit(request, patient_id):

    patient = get_object_or_404(
        Patient,
        patient_id=patient_id,
        is_active=True
    )

    doctors = User.objects.filter(
        profile__role='DOCTOR',
        profile__status='APPROVED'
    ).order_by('first_name')

    if request.method == 'POST':

        full_name = request.POST.get('full_name', '').strip()
        phone = request.POST.get('phone', '').strip()
        date_of_birth = request.POST.get('date_of_birth') or None
        gender = request.POST.get('gender')
        blood_group = request.POST.get('blood_group')
        address = request.POST.get('address', '').strip()
        allergies = request.POST.get('allergies', '').strip()
        medical_history = request.POST.get('medical_history', '').strip()
        doctor_id = request.POST.get('assigned_doctor')

        if not all([full_name, phone, gender]):
            messages.error(request, 'Please fill in all required fields.')

        elif gender not in dict(Patient.GENDER_CHOICES):
            messages.error(request, 'Invalid gender selection.')

        elif blood_group not in dict(Patient.BLOOD_GROUP_CHOICES):
            messages.error(request, 'Invalid blood group selection.')

        else:

            assigned_doctor = None

            if doctor_id:
                assigned_doctor = doctors.filter(id=doctor_id).first()

                if not assigned_doctor:
                    messages.error(request, 'Selected doctor is not available.')
                    return render(
                        request,
                        'core/patient_edit.html',
                        {'patient': patient, 'doctors': doctors}
                    )

            patient.full_name = full_name
            patient.phone = phone
            patient.date_of_birth = date_of_birth
            patient.gender = gender
            patient.blood_group = blood_group
            patient.address = address
            patient.allergies = allergies
            patient.medical_history = medical_history
            patient.assigned_doctor = assigned_doctor

            patient.save()

            messages.success(request, 'Patient information updated successfully.')

            return redirect(
                'patient_detail',
                patient_id=patient.patient_id
            )

    return render(
        request,
        'core/patient_edit.html',
        {
            'patient': patient,
            'doctors': doctors
        }
    )


# =========================
# 

@login_required
@role_required('ADMIN', 'STAFF', 'DOCTOR')
def prescription_detail(request, prescription_id):

    from .models import PharmacySettings

    prescription = get_object_or_404(
        Prescription.objects.select_related(
            'patient',
            'doctor',
            'doctor__profile'
        ).prefetch_related('medicines'),
        prescription_id=prescription_id,
        is_deleted=False
    )

    # Doctor can only view their own prescriptions
    if not request.user.is_superuser:

        if request.user.profile.role == 'DOCTOR':

            if prescription.doctor_id != request.user.id:

                messages.error(
                    request,
                    'You are not authorized to view this prescription.'
                )

                return redirect('doctor_patients')

    # Generate QR only for finalized prescriptions
    qr_code_data = None

    if prescription.status == 'FINALIZED':

        qr_image = generate_prescription_qr(prescription)

        qr_code_data = base64.b64encode(
            qr_image.read()
        ).decode('utf-8')

    # Get pharmacy branding
    pharmacy = PharmacySettings.objects.first()

    print("PHARMACY:", pharmacy)
    print("LOGO FIELD:", pharmacy.logo if pharmacy else "NO PHARMACY")
    print("LOGO URL:", pharmacy.logo.url if pharmacy and pharmacy.logo else "NO LOGO")

    return render(
        request,
        'core/prescription_detail.html',
        {
            'prescription': prescription,
            'qr_code_data': qr_code_data,
            'pharmacy': pharmacy,
        }
    )

# =========================
# PRESCRIPTION LIST
# =========================

@login_required
@role_required('ADMIN', 'STAFF', 'DOCTOR')
def prescription_list(request):

    prescriptions = Prescription.objects.filter(
        is_deleted=False
    ).select_related(
        'patient',
        'doctor'
    ).order_by('-created_at')

    # Doctor can only see their own prescriptions
    if not request.user.is_superuser:

        if request.user.profile.role == 'DOCTOR':

            prescriptions = prescriptions.filter(
                doctor=request.user
            )

    return render(
        request,
        'core/prescription_list.html',
        {
            'prescriptions': prescriptions
        }
    )

# =====================================
# PRESCRIPTION PERMISSION
# =====================================

def can_manage_prescription(user, prescription):

    if user.is_superuser:
        return True

    role = getattr(user.profile, 'role', None)

    if role in ['ADMIN', 'STAFF']:
        return True

    if role == 'DOCTOR' and prescription.doctor_id == user.id:
        return True

    return False


# =====================================
# PRESCRIPTION SNAPSHOT
# =====================================

def create_prescription_snapshot(prescription):

    return {
        'patient': {
            'patient_id': prescription.patient.patient_id,
            'full_name': prescription.patient.full_name,
            'phone': prescription.patient.phone,
        },
        'doctor': prescription.doctor.username,
        'diagnosis': prescription.diagnosis,
        'chief_complaints': prescription.chief_complaints,
        'on_examination': prescription.on_examination,
        'advice': prescription.advice,
        'status': prescription.status,
        'medicines': [
            {
                'medicine_name': medicine.medicine_name,
                'dosage': medicine.dosage,
                'frequency': medicine.frequency,
                'duration': medicine.duration,
                'instructions': medicine.instructions,
            }
            for medicine in prescription.medicines.all()
        ]
    }


# =====================================
# =====================================
# EDIT PRESCRIPTION
# =====================================

@login_required
@role_required('ADMIN', 'STAFF', 'DOCTOR')
def prescription_edit(request, prescription_id):

    prescription = get_object_or_404(
        Prescription.objects.select_related(
            'patient', 'doctor'
        ).prefetch_related('medicines'),
        prescription_id=prescription_id,
        is_deleted=False
    )

    # Permission Check
    if not can_manage_prescription(request.user, prescription):
        messages.error(
            request,
            'You are not authorized to edit this prescription.'
        )
        return redirect('prescription_list')

    if request.method == 'POST':

        reason = request.POST.get('reason', '').strip()

        # Finalized prescription requires reason
        if prescription.status == 'FINALIZED' and not reason:
            messages.error(
                request,
                'Please provide a reason for editing this finalized prescription.'
            )
            return redirect(
                'prescription_edit',
                prescription_id=prescription_id
            )

        medicine_names = request.POST.getlist('medicine_name[]')
        dosages = request.POST.getlist('dosage[]')
        frequencies = request.POST.getlist('frequency[]')
        durations = request.POST.getlist('duration[]')
        instructions = request.POST.getlist('instructions[]')

        # Validate medicine entries
        valid_medicines = [
            i for i, name in enumerate(medicine_names)
            if name.strip()
        ]

        if not valid_medicines:
            messages.error(
                request,
                'At least one medicine is required.'
            )
            return redirect(
                'prescription_edit',
                prescription_id=prescription_id
            )

        try:

            with transaction.atomic():

                # Preserve previous prescription data
                old_snapshot = create_prescription_snapshot(
                    prescription
                )

                # Save version history
                PrescriptionVersion.objects.create(
                    prescription=prescription,
                    prescription_id_snapshot=prescription.prescription_id,
                    action='EDIT',
                    snapshot={
                        'reason': reason,
                        'previous_data': old_snapshot,
                    },
                    changed_by=request.user
                )

                # Update clinical information
                prescription.diagnosis = request.POST.get(
                    'diagnosis', ''
                ).strip()

                prescription.chief_complaints = request.POST.get(
                    'chief_complaints', ''
                ).strip()

                prescription.on_examination = request.POST.get(
                    'on_examination', ''
                ).strip()

                prescription.advice = request.POST.get(
                    'advice', ''
                ).strip()

                prescription.save()

                # Replace medicines
                prescription.medicines.all().delete()

                for i in valid_medicines:

                    PrescriptionMedicine.objects.create(
                        prescription=prescription,
                        medicine_name=medicine_names[i].strip(),
                        dosage=dosages[i].strip() if i < len(dosages) else '',
                        frequency=frequencies[i].strip() if i < len(frequencies) else '',
                        duration=durations[i].strip() if i < len(durations) else '',
                        instructions=instructions[i].strip() if i < len(instructions) else ''
                    )

            messages.success(
                request,
                'Prescription updated successfully. Previous version saved in history.'
            )

            return redirect(
                'prescription_detail',
                prescription_id=prescription.prescription_id
            )

        except Exception:
            messages.error(
                request,
                'Something went wrong. Prescription was not updated.'
            )

            return redirect(
                'prescription_edit',
                prescription_id=prescription_id
            )

    return render(
        request,
        'core/prescription_edit.html',
        {'prescription': prescription}
    )

# =====================================
# =====================================
# DELETE PRESCRIPTION (SOFT DELETE)
# =====================================

@login_required
@role_required('ADMIN', 'STAFF', 'DOCTOR')
def prescription_delete(request, prescription_id):

    prescription = get_object_or_404(
        Prescription.objects.select_related(
            'patient', 'doctor'
        ),
        prescription_id=prescription_id,
        is_deleted=False
    )

    # Permission Check
    if not can_manage_prescription(request.user, prescription):
        messages.error(
            request,
            'You are not authorized to delete this prescription.'
        )
        return redirect('prescription_list')

    if request.method == 'POST':

        reason = request.POST.get('reason', '').strip()

        # Finalized prescription requires deletion reason
        if prescription.status == 'FINALIZED' and not reason:
            messages.error(
                request,
                'Please provide a reason for deleting this finalized prescription.'
            )
            return redirect(
                'prescription_delete',
                prescription_id=prescription.prescription_id
            )

        try:

            with transaction.atomic():

                # Lock prescription during deletion
                prescription = get_object_or_404(
                    Prescription.objects.select_for_update(),
                    prescription_id=prescription_id,
                    is_deleted=False
                )

                # Preserve previous data
                snapshot = create_prescription_snapshot(
                    prescription
                )

                # Save deletion history
                PrescriptionVersion.objects.create(
                    prescription=prescription,
                    prescription_id_snapshot=prescription.prescription_id,
                    action='DELETE',
                    snapshot={
                        'reason': reason,
                        'previous_data': snapshot,
                    },
                    changed_by=request.user
                )

                # Soft Delete
                prescription.is_deleted = True
                prescription.deleted_at = timezone.now()
                prescription.save(
                    update_fields=['is_deleted', 'deleted_at']
                )

            messages.success(
                request,
                'Prescription deleted safely. Previous information has been preserved in Version History.'
            )

            return redirect('prescription_list')

        except Exception:
            messages.error(
                request,
                'Something went wrong. Prescription was not deleted.'
            )

            return redirect(
                'prescription_detail',
                prescription_id=prescription_id
            )

    return render(
        request,
        'core/prescription_delete.html',
        {'prescription': prescription}
    )
# =====================================
# =====================================
# RESTORE DELETED PRESCRIPTION
# =====================================

@login_required
@role_required('ADMIN', 'STAFF')
def prescription_restore(request, prescription_id):

    prescription = get_object_or_404(
        Prescription.objects.select_related(
            'patient',
            'doctor'
        ),
        prescription_id=prescription_id,
        is_deleted=True
    )

    if request.method == 'POST':

        reason = request.POST.get('reason', '').strip()

        if not reason:
            messages.error(
                request,
                'Please provide a reason for restoring this prescription.'
            )
            return redirect(
                'prescription_restore',
                prescription_id=prescription_id
            )

        try:

            with transaction.atomic():

                # Lock prescription to prevent duplicate restoration
                locked_prescription = (
                    Prescription.objects.select_for_update()
                    .select_related('patient', 'doctor')
                    .filter(
                        prescription_id=prescription_id,
                        is_deleted=True
                    )
                    .first()
                )

                if not locked_prescription:

                    messages.warning(
                        request,
                        'This prescription has already been restored.'
                    )

                    return redirect('deleted_prescription_list')

                # Preserve previous data
                previous_snapshot = create_prescription_snapshot(
                    locked_prescription
                )

                # Save restoration history
                PrescriptionVersion.objects.create(
                    prescription=locked_prescription,
                    prescription_id_snapshot=locked_prescription.prescription_id,
                    action='RESTORE',
                    snapshot={
                        'reason': reason,
                        'previous_data': previous_snapshot,
                    },
                    changed_by=request.user
                )

                # Restore prescription
                locked_prescription.is_deleted = False
                locked_prescription.deleted_at = None

                locked_prescription.save(
                    update_fields=[
                        'is_deleted',
                        'deleted_at',
                        'updated_at'
                    ]
                )

            messages.success(
                request,
                'Prescription successfully restored. Restoration history has been saved.'
            )

            return redirect(
                'prescription_detail',
                prescription_id=prescription_id
            )

        except Exception:
            messages.error(
                request,
                'Something went wrong. Prescription was not restored.'
            )

            return redirect(
                'prescription_restore',
                prescription_id=prescription_id
            )

    return render(
        request,
        'core/prescription_restore.html',
        {
            'prescription': prescription
        }
    )
# =====================================
# DELETED PRESCRIPTION LIST
# =====================================

@login_required
@role_required('ADMIN', 'STAFF')
def deleted_prescription_list(request):

    prescriptions = Prescription.objects.filter(
        is_deleted=True
    ).select_related(
        'patient',
        'doctor'
    ).order_by('-deleted_at')

    return render(
        request,
        'core/deleted_prescription_list.html',
        {
            'prescriptions': prescriptions
        }
    )

# =====================================
# PUBLIC PRESCRIPTION QR VERIFICATION
# =====================================

def verify_prescription(request, token):

    prescription = Prescription.objects.filter(
        verification_token=token,
        status='FINALIZED',
        is_deleted=False
    ).select_related(
        'doctor',
        'doctor__profile'
    ).first()

    if not prescription:
        return render(
            request,
            'core/prescription_verification.html',
            {
                'verified': False
            }
        )

    return render(
        request,
        'core/prescription_verification.html',
        {
            'verified': True,
            'prescription': prescription
        }
    )
# =====================================
# PRESCRIPTION VERSION HISTORY
# =====================================

@login_required
@role_required('ADMIN', 'STAFF', 'DOCTOR')
def prescription_history(request, prescription_id):

    prescription = get_object_or_404(
        Prescription.objects.select_related(
            'patient',
            'doctor'
        ),
        prescription_id=prescription_id
    )

    # Doctor can only view their own prescription history
    if not request.user.is_superuser:

        if request.user.profile.role == 'DOCTOR':

            if prescription.doctor_id != request.user.id:

                messages.error(
                    request,
                    'You are not authorized to view this prescription history.'
                )

                return redirect('doctor_patients')

    # Get all previous versions
    versions = PrescriptionVersion.objects.filter(
        prescription_id_snapshot=prescription.prescription_id
    ).select_related(
        'changed_by'
    ).order_by('-changed_at')

    return render(
        request,
        'core/prescription_history.html',
        {
            'prescription': prescription,
            'versions': versions,
        }
    )