from functools import wraps

from django.contrib.auth.models import AnonymousUser
from django.http import HttpResponseForbidden, HttpResponse


# @method_decorator(admin_user_required())
def admin_user_required():
    def decorator(func):
        @wraps(func)
        def check_user_role(request, *args, **kwargs):
            user = request.user
            if not isinstance(user, AnonymousUser):
                if user.is_admin_user:
                    res = func(request, *args, **kwargs)
                    return res
                else:
                    return HttpResponseForbidden()
            else:
                return HttpResponse(status=401)

        return check_user_role

    return decorator


def merchant_user_required():
    def decorator(func):
        @wraps(func)
        def check_user_role(request, *args, **kwargs):
            user = request.user
            if not isinstance(user, AnonymousUser):
                if user.is_merchant_user:
                    res = func(request, *args, **kwargs)
                    return res
                else:
                    return HttpResponseForbidden()
            else:
                return HttpResponse(status=401)

        return check_user_role

    return decorator


def frontend_user_required():
    def decorator(func):
        @wraps(func)
        def check_user_role(request, *args, **kwargs):
            user = request.user
            if not user or isinstance(user, AnonymousUser):
                return HttpResponse(status=401)
            else:
                res = func(request, *args, **kwargs)
                return res if user.is_frontend_user else HttpResponseForbidden()

        return check_user_role

    return decorator


def permission_required(perm_required=None):
    def decorator(func):
        @wraps(func)
        def check_perms(request, *args, **kwargs):
            user = request.user
            if not isinstance(user, AnonymousUser):
                if perm_required:
                    print('permission_required =', user.has_perm(perm_required))
                    if user.has_perm(perm_required) is False:
                        return HttpResponseForbidden()
                    else:
                        res = func(request, *args, **kwargs)
                        return res
                else:
                    res = func(request, *args, **kwargs)
                    return res
            else:
                return HttpResponse(status=401)

        return check_perms

    return decorator
