from django.contrib.staticfiles.urls import urlpatterns
from django.urls import path

from . import views

urlpatterns = [
    path ('api/vads/ipn/', views.api_vads_ipn, name='api_vads_ipn'),
]