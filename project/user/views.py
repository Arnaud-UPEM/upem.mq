from django.contrib.auth import authenticate
from django.shortcuts import redirect, render

from wagtail.documents.views import serve

from .forms import LoginForm
from .models import Auth

# Create your views here.
