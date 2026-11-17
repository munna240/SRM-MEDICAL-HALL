
import uuid

from django.db import models
from django.contrib.auth.models import User


# =====================================
# PATIENT
# =====================================

class Patient(models.Model):

    GENDER_CHOICES = [
        ('MALE', 'Male'),
        ('FEMALE', 'Female'),
        ('OTHER', 'Other'),
    ]

    BLOOD_GROUP_CHOICES = [
        ('A+', 'A+'),
        ('A-', 'A-'),
        ('B+', 'B+'),
        ('B-', 'B-'),
        ('O+', 'O+'),
        ('O-', 'O-'),
        ('AB+', 'AB+'),
        ('AB-', 'AB-'),
        ('UNKNOWN', 'Unknown'),
    ]

    patient_id = models.CharField(
        max_length=20,
        unique=True,
        editable=False
    )

    full_name = models.CharField(max_length=200)
    phone = models.CharField(max_length=20)
    date_of_birth = models.DateField(null=True, blank=True)

    gender = models.CharField(
        max_length=10,
        choices=GENDER_CHOICES
    )

    blood_group = models.CharField(
        max_length=10,
        choices=BLOOD_GROUP_CHOICES,
        default='UNKNOWN'
    )

    address = models.TextField(blank=True)

    allergies = models.TextField(
        blank=True,
        help_text="Known medicine or food allergies"
    )

    medical_history = models.TextField(blank=True)

    assigned_doctor = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='assigned_patients'
    )

    created_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='registered_patients'
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)

    def save(self, *args, **kwargs):

        if not self.patient_id:
            self.patient_id = 'SRM-' + uuid.uuid4().hex[:8].upper()

        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.patient_id} - {self.full_name}"

    class Meta:
        ordering = ['-created_at']


# =====================================
# DIGITAL PRESCRIPTION
# =====================================

class Prescription(models.Model):

    STATUS_CHOICES = [
        ('DRAFT', 'Draft'),
        ('FINALIZED', 'Finalized'),
    ]

    prescription_id = models.CharField(
        max_length=30,
        unique=True,
        editable=False
    )

    # Unique secure token for QR verification
    verification_token = models.UUIDField(
        default=uuid.uuid4,
        unique=True,
        editable=False
    )

    patient = models.ForeignKey(
        Patient,
        on_delete=models.PROTECT,
        related_name='prescriptions'
    )

    doctor = models.ForeignKey(
        User,
        on_delete=models.PROTECT,
        related_name='doctor_prescriptions'
    )

    created_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name='created_prescriptions'
    )

    diagnosis = models.TextField(blank=True)

    chief_complaints = models.TextField(
        blank=True,
        verbose_name="C/C (Chief Complaints)"
    )

    on_examination = models.TextField(
        blank=True,
        verbose_name="O/E (On Examination)"
    )

    advice = models.TextField(
        blank=True,
        verbose_name="Adv (Advice)"
    )

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='DRAFT'
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    finalized_at = models.DateTimeField(
        null=True,
        blank=True
    )

    # Soft Delete
    is_deleted = models.BooleanField(default=False)
    deleted_at = models.DateTimeField(null=True, blank=True)

    def save(self, *args, **kwargs):

        if not self.prescription_id:
            self.prescription_id = (
                'RX-' + uuid.uuid4().hex[:10].upper()
            )

        super().save(*args, **kwargs)

    def __str__(self):
        return self.prescription_id

    class Meta:
        ordering = ['-created_at']


# =====================================
# PRESCRIPTION MEDICINES
# =====================================

class PrescriptionMedicine(models.Model):

    prescription = models.ForeignKey(
        Prescription,
        on_delete=models.CASCADE,
        related_name='medicines'
    )

    medicine_name = models.CharField(max_length=255)
    dosage = models.CharField(max_length=100)
    frequency = models.CharField(max_length=100)
    duration = models.CharField(max_length=100)
    instructions = models.TextField(blank=True)

    def __str__(self):
        return self.medicine_name


# =====================================
# PRESCRIPTION VERSION HISTORY
# =====================================

class PrescriptionVersion(models.Model):

    ACTION_CHOICES = [
        ('EDIT', 'Edited'),
        ('DELETE', 'Deleted'),
        ('RESTORE', 'Restored'),
    ]

    prescription = models.ForeignKey(
        Prescription,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='versions'
    )

    prescription_id_snapshot = models.CharField(max_length=30)

    action = models.CharField(
        max_length=20,
        choices=ACTION_CHOICES
    )

    snapshot = models.JSONField(default=dict)

    changed_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )

    changed_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-changed_at']

    def __str__(self):
        return f"{self.prescription_id_snapshot} - {self.action}"

# =====================================
# PHARMACY WEBSITE SETTINGS
# =====================================

class PharmacySettings(models.Model):

    pharmacy_name = models.CharField(
        max_length=200,
        default="SRM MEDICAL HALL"
    )

    logo = models.ImageField(
        upload_to="pharmacy/",
        blank=True,
        null=True
    )

    address = models.TextField(blank=True)

    phone = models.CharField(
        max_length=30,
        blank=True
    )

    email = models.EmailField(blank=True)

    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.pharmacy_name
