
import uuid

from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages

from core.models import (
    Patient,
    Prescription,
    PrescriptionMedicine,
    PharmacySettings
)

from .decorators import role_required
from .forms import StaffRegistrationForm, DoctorRegistrationForm
from .models import UserProfile


# =========================
# LOGIN
# =========================

def login_view(request):

    if request.method == 'POST':

        username = request.POST.get('username')
        password = request.POST.get('password')
        selected_role = request.POST.get('role')

        user = authenticate(
            request,
            username=username,
            password=password
        )

        if user is not None:

            authorized = False

            if user.is_superuser and selected_role == 'ADMIN':
                authorized = True

            elif hasattr(user, 'profile'):

                profile = user.profile

                if profile.role == selected_role:

                    if profile.status == 'APPROVED':
                        authorized = True

                    elif profile.status == 'PENDING':
                        messages.warning(
                            request,
                            'Your registration is pending Admin approval.'
                        )

                    elif profile.status == 'REJECTED':
                        messages.error(
                            request,
                            'Your registration application has been rejected. Please contact Admin.'
                        )

            if authorized:
                login(request, user)
                return redirect('dashboard')

            elif not any(
                message.level == messages.WARNING or
                message.level == messages.ERROR
                for message in messages.get_messages(request)
            ):
                messages.error(
                    request,
                    'You are not authorized to access this portal.'
                )

        else:
            messages.error(
                request,
                'Invalid username or password.'
            )

    # Pharmacy Settings থেকে Logo ও Name নেওয়া
    pharmacy = PharmacySettings.objects.first()

    return render(
        request,
        'accounts/login.html',
        {
            'pharmacy': pharmacy
        }
    )


# =========================
# DASHBOARD
# =========================

@login_required
@role_required('ADMIN', 'STAFF', 'DOCTOR')
def dashboard_view(request):

    if request.user.is_superuser:
        role = 'ADMIN'

    elif hasattr(request.user, 'profile'):

        profile = request.user.profile

        if profile.status != 'APPROVED':
            logout(request)
            messages.warning(
                request,
                'Your account is not approved yet.'
            )
            return redirect('login')

        role = profile.role

    else:
        logout(request)
        return redirect('login')

    return render(
        request,
        'accounts/dashboard.html',
        {'role': role}
    )


# =========================
# LOGOUT
# =========================

def logout_view(request):

    logout(request)

    return redirect('login')


# =========================
# STAFF REGISTRATION
# =========================

def staff_register(request):

    form = StaffRegistrationForm(
        request.POST or None,
        request.FILES or None
    )

    if request.method == 'POST' and form.is_valid():

        data = form.cleaned_data

        user = User.objects.create_user(
            username=data['username'],
            email=data['email'],
            password=data['password'],
            first_name=data['first_name'],
            last_name=data['last_name']
        )

        UserProfile.objects.create(
            user=user,
            role='STAFF',
            status='PENDING',
            phone=data['phone'],
            address=data['address'],
            profile_picture=data.get('profile_picture')
        )

        messages.success(
            request,
            'Staff registration successful! Please wait for Admin approval.'
        )

        return redirect('login')

    return render(
        request,
        'accounts/register.html',
        {
            'form': form,
            'role': 'Staff'
        }
    )


# =========================
# DOCTOR REGISTRATION
# =========================

def doctor_register(request):

    form = DoctorRegistrationForm(
        request.POST or None,
        request.FILES or None
    )

    if request.method == 'POST' and form.is_valid():

        data = form.cleaned_data

        user = User.objects.create_user(
            username=data['username'],
            email=data['email'],
            password=data['password'],
            first_name=data['first_name'],
            last_name=data['last_name']
        )

        UserProfile.objects.create(
            user=user,
            role='DOCTOR',
            status='PENDING',
            phone=data['phone'],
            address=data['address'],
            profile_picture=data.get('profile_picture'),
            qualification=data['qualification'],
            specialization=data['specialization'],
            bmdc_number=data['bmdc_number'],
            signature=data.get('signature')
        )

        messages.success(
            request,
            'Doctor registration successful! Please wait for Admin approval.'
        )

        return redirect('login')

    return render(
        request,
        'accounts/register.html',
        {
            'form': form,
            'role': 'Doctor'
        }
    )


# =========================
# DOCTOR PROFILE
# =========================

@login_required
@role_required('DOCTOR')
def doctor_profile(request):

    profile = request.user.profile

    return render(
        request,
        'accounts/doctor_profile.html',
        {'profile': profile}
    )


# =========================
# EDIT DOCTOR PROFILE
# =========================

@login_required
@role_required('DOCTOR')
def doctor_profile_edit(request):

    profile = request.user.profile

    if request.method == 'POST':

        request.user.first_name = request.POST.get(
            'first_name', ''
        ).strip()

        request.user.last_name = request.POST.get(
            'last_name', ''
        ).strip()

        request.user.save()

        profile.phone = request.POST.get('phone', '').strip()
        profile.address = request.POST.get('address', '').strip()
        profile.qualification = request.POST.get('qualification', '').strip()
        profile.specialization = request.POST.get('specialization', '').strip()
        profile.bmdc_number = request.POST.get('bmdc_number', '').strip()

        if request.FILES.get('profile_picture'):
            profile.profile_picture = request.FILES['profile_picture']

        if request.FILES.get('signature'):
            profile.signature = request.FILES['signature']

        profile.save()

        messages.success(
            request,
            'Your profile has been updated successfully.'
        )

        return redirect('doctor_profile')

    return render(
        request,
        'accounts/doctor_profile_edit.html',
        {'profile': profile}
    )


# =========================
# DOCTOR MY PATIENTS
# =========================

@login_required
@role_required('DOCTOR')
def doctor_patients(request):

    patients = Patient.objects.filter(
        assigned_doctor=request.user,
        is_active=True
    ).order_by('-created_at')

    return render(
        request,
        'accounts/doctor_patients.html',
        {
            'patients': patients
        }
    )


# =========================
# DOCTOR PATIENT DETAILS
# =========================

@login_required
@role_required('DOCTOR')
def doctor_patient_detail(request, patient_id):

    patient = get_object_or_404(
        Patient,
        patient_id=patient_id,
        assigned_doctor=request.user,
        is_active=True
    )

    prescriptions = Prescription.objects.filter(
        patient=patient,
        doctor=request.user,
        is_deleted=False
    ).prefetch_related(
        'medicines'
    ).order_by('-created_at')

    return render(
        request,
        'accounts/doctor_patient_detail.html',
        {
            'patient': patient,
            'prescriptions': prescriptions
        }
    )


# =========================
# DOCTOR CREATE PRESCRIPTION
# =========================

@login_required
@role_required('DOCTOR')
def doctor_create_prescription(request, patient_id):

    patient = get_object_or_404(
        Patient,
        patient_id=patient_id,
        assigned_doctor=request.user,
        is_active=True
    )

    if request.method == 'POST':

        action = request.POST.get('action', 'draft')

        if action not in ['draft', 'finalize']:
            messages.error(
                request,
                'Invalid prescription action.'
            )

            return redirect(
                'doctor_patient_detail',
                patient_id=patient.patient_id
            )

        prescription = Prescription.objects.create(
            patient=patient,
            doctor=request.user,
            created_by=request.user,
            diagnosis=request.POST.get('diagnosis', '').strip(),
            chief_complaints=request.POST.get('chief_complaints', '').strip(),
            on_examination=request.POST.get('on_examination', '').strip(),
            advice=request.POST.get('advice', '').strip(),
            status='FINALIZED' if action == 'finalize' else 'DRAFT',
            finalized_at=timezone.now() if action == 'finalize' else None
        )

        medicine_names = request.POST.getlist('medicine_name[]')
        dosages = request.POST.getlist('dosage[]')
        frequencies = request.POST.getlist('frequency[]')
        durations = request.POST.getlist('duration[]')
        instructions = request.POST.getlist('instructions[]')

        for i in range(len(medicine_names)):

            if medicine_names[i].strip():

                PrescriptionMedicine.objects.create(
                    prescription=prescription,
                    medicine_name=medicine_names[i].strip(),
                    dosage=dosages[i].strip() if i < len(dosages) else '',
                    frequency=frequencies[i].strip() if i < len(frequencies) else '',
                    duration=durations[i].strip() if i < len(durations) else '',
                    instructions=instructions[i].strip() if i < len(instructions) else ''
                )

        if action == 'finalize':
            messages.success(
                request,
                'Prescription finalized successfully!'
            )

        else:
            messages.success(
                request,
                'Prescription saved successfully as Draft.'
            )

        return redirect(
            'doctor_patient_detail',
            patient_id=patient.patient_id
        )

    return render(
        request,
        'accounts/doctor_create_prescription.html',
        {'patient': patient}
    )


# =====================================
# DOCTOR CREATES PRESCRIPTION FOR NEW PATIENT
# =====================================

@login_required
@role_required('DOCTOR')
def doctor_new_patient_prescription(request):

    if request.method == 'POST':

        action = request.POST.get('action', 'draft')

        if action not in ['draft', 'finalize']:

            messages.error(
                request,
                'Invalid prescription action.'
            )

            return redirect('doctor_new_patient_prescription')

        full_name = request.POST.get('full_name', '').strip()
        phone = request.POST.get('phone', '').strip()
        gender = request.POST.get('gender', '').strip()

        if not full_name or not phone or gender not in [
            'MALE',
            'FEMALE',
            'OTHER'
        ]:

            messages.error(
                request,
                'Please provide valid patient information.'
            )

            return redirect('doctor_new_patient_prescription')

        patient = Patient.objects.create(
            full_name=full_name,
            phone=phone,
            date_of_birth=request.POST.get('date_of_birth') or None,
            gender=gender,
            blood_group=request.POST.get('blood_group', 'UNKNOWN'),
            address=request.POST.get('address', '').strip(),
            allergies=request.POST.get('allergies', '').strip(),
            medical_history=request.POST.get('medical_history', '').strip(),
            assigned_doctor=request.user,
            created_by=request.user
        )

        prescription = Prescription.objects.create(
            patient=patient,
            doctor=request.user,
            created_by=request.user,
            diagnosis=request.POST.get('diagnosis', '').strip(),
            chief_complaints=request.POST.get('chief_complaints', '').strip(),
            on_examination=request.POST.get('on_examination', '').strip(),
            advice=request.POST.get('advice', '').strip(),
            status='FINALIZED' if action == 'finalize' else 'DRAFT',
            finalized_at=timezone.now() if action == 'finalize' else None
        )

        medicine_names = request.POST.getlist('medicine_name[]')
        dosages = request.POST.getlist('dosage[]')
        frequencies = request.POST.getlist('frequency[]')
        durations = request.POST.getlist('duration[]')
        instructions = request.POST.getlist('instructions[]')

        for i in range(len(medicine_names)):

            if medicine_names[i].strip():

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
            'New patient and prescription created successfully!'
        )

        return redirect(
            'doctor_patient_detail',
            patient_id=patient.patient_id
        )

    return render(
        request,
        'accounts/doctor_new_patient_prescription.html'
    )
