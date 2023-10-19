from django.urls import path

from  brainstorm.views import index

app_name = "brainstorm"

urlpatterns = [
    path('', index),
]