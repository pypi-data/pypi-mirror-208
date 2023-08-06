from django.conf import settings
from django.http import HttpResponse
from django.shortcuts import redirect
from django.urls import reverse

from django.contrib.auth import get_user_model
def start_reg(request,url_only=True):
    request.session["JP_OP_MODE"] = "REG"
    USERNAME_FIELD = getattr(settings, "OIDC_USERNAME_FIELD",'username')
    request.session["token"] = getattr(request.user,USERNAME_FIELD)
    request.session.modified = 1
    if url_only:
        return HttpResponse(reverse('oidc_authentication_init'))
    return redirect('oidc_authentication_init')


def start_oidc_sign(request,url_only=True):
    u = request.session.get("username")
    if u:
        User = get_user_model()
        USERNAME_FIELD = getattr(settings, "OIDC_USERNAME_FIELD", 'username')
        user = User.objects.get(username=u)
        request.session["token"] = getattr(user, USERNAME_FIELD)
    request.session["JP_OP_MODE"] = "LOGIN"
    request.session.modified = 1
    if url_only:
        return HttpResponse(reverse('oidc_authentication_init'))
    return redirect("oidc_authentication_init")


