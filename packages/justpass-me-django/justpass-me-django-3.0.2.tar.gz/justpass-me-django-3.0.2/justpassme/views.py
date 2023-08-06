from django.shortcuts import render

from django.conf import settings
from .utils import import_mod


def enroll(request):
    return render(request,'amwal-auth.html',{})


def start_reg(request,url_only=True):
    from justpassme.helpers import start_reg
    return start_reg(request,url_only)


def start_login(request,url_only=True):
    from justpassme.helpers import start_oidc_sign
    return start_oidc_sign(request,url_only)

def success(request):
    op_mode = request.session.pop("JP_OP_MODE","LOGIN")
    if op_mode == "LOGIN":
        return import_mod(settings.AUTHENTICATION_SUCCESS)(request)
    elif op_mode == "REG":
        return import_mod(settings.REGISTRATION_SUCCESS)(request)


def failure(request):
    op_mode = request.session.pop("JP_OP_MODE","LOGIN")
    if op_mode == "LOGIN":
        return import_mod(settings.AUTHENTICATION_FAILURE)(request)
    elif op_mode == "REG":
        return import_mod(settings.REGISTRATION_FAILURE)(request)
