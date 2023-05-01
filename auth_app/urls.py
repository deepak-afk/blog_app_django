from django.urls import path
from django.contrib.auth import views as auth_views
from django.urls import path
from .views import signup_process, login_process, dashboard, logout_process
from . import views

urlpatterns = [
    path('signup/', signup_process, name='signup_process'),
    path('login/', login_process, name='login_process'),
    path('dashboard/', dashboard, name='dashboard'),
    path('logout/', logout_process, name='logout_process'),
]
