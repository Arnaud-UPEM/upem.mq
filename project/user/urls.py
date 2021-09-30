from django.urls import path
from django.contrib.auth import views as auth_views

from . import views

# app_name = 'user'

urlpatterns = [
    path('mdp_oublie/', auth_views.PasswordResetView.as_view(), name='password_reset'),
    path('mdp_oublie/fin/', auth_views.PasswordResetDoneView.as_view(), name='password_reset_done'),
    path('mdp/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(), name='password_reset_confirm'),
    path('mdp/fin/', auth_views.PasswordResetCompleteView.as_view(), name='password_reset_complete'),
]