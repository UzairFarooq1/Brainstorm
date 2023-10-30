from django.urls import path
from . import views
from django.contrib import admin
from django.contrib.auth.views import LogoutView


urlpatterns = [
    path('', views.admin_dashboard, name='admin_dashboard'),
    path('panel', views.admin_dashboard, name='admin_dashboard'),
    path('panellogout/', LogoutView.as_view(), name='admin_logout'),

    # Add more custom admin URLs as needed
]
