from django.urls import path
from . import views
from django.contrib import admin


urlpatterns = [
    path('', views.admin_dashboard, name='admin_dashboard'),
    path('panel', views.admin_dashboard, name='admin_dashboard'),

    # Add more custom admin URLs as needed
]
