from functools import wraps
from django.shortcuts import redirect, resolve_url
from django.conf import settings
from django.contrib.auth import REDIRECT_FIELD_NAME
from django.utils.http import urlencode
from django.contrib.auth import login
from django.contrib.auth.views import redirect_to_login
from django.http import HttpResponseForbidden

def role_required(roles, redirect_to_portal=True):
    

    if isinstance(roles, str):
        roles_list = [roles]
    else:
        roles_list = list(roles)

    def decorator(view_func):
        @wraps(view_func)
        def _wrapped(request, *args, **kwargs):
            if not request.user.is_authenticated:
                login_url = resolve_url(settings.LOGIN_URL)
                return redirect_to_login(request.get_full_path(), login_url)
            user_rol = getattr(request.user, "rol", None)
            if user_rol not in roles_list:
                if redirect_to_portal:
                    return redirect("main:redirigir_por_rol")
                else:
                    return HttpResponseForbidden("Acceso denegado")
            return view_func(request, *args, **kwargs)
        return _wrapped
    return decorator
