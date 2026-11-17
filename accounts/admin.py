
from django.contrib import admin
from .models import UserProfile


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):

    list_display = (
        'user',
        'role',
        'phone',
        'status',
        'created_at',
    )

    list_filter = ('role', 'status')

    search_fields = (
        'user__username',
        'user__first_name',
        'user__last_name',
        'phone',
        'bmdc_number',
    )

    actions = ['approve_applications', 'reject_applications']

    @admin.action(description='Approve selected applications')
    def approve_applications(self, request, queryset):
        queryset.update(
            status='APPROVED',
            rejection_reason=''
        )

    @admin.action(description='Reject selected applications')
    def reject_applications(self, request, queryset):
        queryset.update(status='REJECTED')
