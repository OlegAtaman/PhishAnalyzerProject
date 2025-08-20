from django.urls import path

from authapp.views import login_user, logout_user, register_user

urlpatterns = [
    path('login_user/', login_user, name='login_user'),
    path('logout_user/', logout_user, name='logout_user'),
    path('register_user/', register_user, name='register_user')
]