from django.urls import path
from . import views

app_name = "justpass"
urlpatterns = [
    path('reg/redirect/', views.start_reg, name="get_reg_link",kwargs={"url_only":True}),
    path('reg/', views.start_reg, name="start_reg",kwargs={"url_only":False}),
    path('login/redirect/', views.start_login, name="start_login", kwargs={"url_only": False}),
    path('login/', views.start_login, name="get_login_link",kwargs={"url_only":True}),
    path('enroll/', views.enroll, name="enroll_justpass"),
    path('success/', views.success, name="OIDC_success"),
    path('failure/', views.failure, name="OIDC_failure"),
    path('fail/', views.failure, name="OIDC_fail"),
    ]