
from functools import wraps
from django.shortcuts import redirect
from django.contrib import messages


def role_required(*allowed_roles):

    def decorator(view_func):

        @wraps(view_func)
        def wrapper(request, *args, **kwargs):

            user = request.user

            if not user.is_authenticated:
                return redirect('login')

            # Admin Access
            if user.is_superuser and 'ADMIN' in allowed_roles:
                return view_func(request, *args, **kwargs)

            # Staff / Doctor Access
            if hasattr(user, 'profile'):

                profile = user.profile

                if (
                    profile.status == 'APPROVED'
                    and profile.role in allowed_roles
                ):
                    return view_func(request, *args, **kwargs)

            messages.error(
                request,
                'You are not authorized to access this page.'
            )

            return redirect('dashboard')

        return wrapper

    return decorator
