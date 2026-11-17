
from django.db import models
from django.contrib.auth.models import User


class UserProfile(models.Model):

    ROLE_CHOICES = [
        ('STAFF', 'Staff'),
        ('DOCTOR', 'Doctor'),
    ]

    STATUS_CHOICES = [
        ('PENDING', 'Pending Approval'),
        ('APPROVED', 'Approved'),
        ('REJECTED', 'Rejected'),
    ]

    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='profile'
    )

    role = models.CharField(
        max_length=20,
        choices=ROLE_CHOICES
    )

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='PENDING'
    )

    phone = models.CharField(max_length=20)
    address = models.TextField(blank=True)

    profile_picture = models.ImageField(
        upload_to='profiles/',
        blank=True,
        null=True
    )

    # Doctor Information
    qualification = models.CharField(
        max_length=255,
        blank=True
    )

    specialization = models.CharField(
        max_length=255,
        blank=True
    )

    bmdc_number = models.CharField(
        max_length=100,
        blank=True
    )

    signature = models.ImageField(
        upload_to='doctor_signatures/',
        blank=True,
        null=True
    )

    seal = models.ImageField(
        upload_to='doctor_seals/',
        blank=True,
        null=True
    )

    rejection_reason = models.TextField(blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.role} - {self.status}"
