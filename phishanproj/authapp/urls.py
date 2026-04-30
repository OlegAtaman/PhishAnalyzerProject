from django.urls import path
from django.contrib.auth import views as auth_views
from authapp.views import login_user, logout_user, register_user, enter_email, confirm_email, profile_user

urlpatterns = [
    path('login_user/', login_user, name='login_user'),
    path('logout_user/', logout_user, name='logout_user'),
    path('register_user/', register_user, name='register_user'),
    path('enter_email/', enter_email, name='enter_email'),
    path('confirm_email/', confirm_email, name='confirm_email'),
    path('profile/<name>/', profile_user, name='profile_user'),
    path('password-reset/',
         auth_views.PasswordResetView.as_view(
             template_name='authapp/password_reset.html'
         ),
         name='password_reset'),
    path('password-reset/done/',
         auth_views.PasswordResetDoneView.as_view(
             template_name='authapp/password_reset_done.html'
         ),
         name='password_reset_done'),
    path(
        'reset/<uidb64>/<token>/',
        auth_views.PasswordResetConfirmView.as_view(
            template_name='authapp/password_reset_confirm.html'
        ),
        name='password_reset_confirm'
    ),
    path(
        'reset/<uidb64>/set-password/',
        auth_views.PasswordResetConfirmView.as_view(
            template_name='authapp/password_reset_confirm.html'
        ),
    ),
    path('reset/done/',
         auth_views.PasswordResetCompleteView.as_view(
             template_name='authapp/password_reset_complete.html'
         ),
         name='password_reset_complete'),
]