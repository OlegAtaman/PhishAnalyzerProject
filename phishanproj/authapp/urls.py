from django.urls import path

from authapp.views import login_user, logout_user, register_user, enter_email, confirm_email, profile_user

urlpatterns = [
    path('login_user/', login_user, name='login_user'),
    path('logout_user/', logout_user, name='logout_user'),
    path('register_user/', register_user, name='register_user'),
    path('enter_email/', enter_email, name='enter_email'),
    path('confirm_email/', confirm_email, name='confirm_email'),
    path('profile/<name>/', profile_user, name='profile_user'),
]