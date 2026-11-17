
from .models import PharmacySettings


def pharmacy_settings(request):
    settings = PharmacySettings.objects.first()

    return {
        "pharmacy": settings
    }
