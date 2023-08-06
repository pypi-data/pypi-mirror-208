from django.urls import path
from . import views

urlpatterns = [
    path('reg/', views.start_reg, name="start_justpass_reg"),
    path('login/redirect/', views.start_login, name="goto_justpass_login", kwargs={"url_only": False}),
    path('login/', views.start_login, name="start_justpass_login",kwargs={"url_only":True}),
    path('enroll/', views.enroll, name="enroll_justpass"),
    path('success/', views.success, name="OIDC_success"),
    path('failure/', views.failure, name="OIDC_failure"),
    path('fail/', views.failure, name="OIDC_fail"),
    ]