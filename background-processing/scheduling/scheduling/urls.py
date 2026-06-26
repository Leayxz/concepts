from django.urls import path
from . import views

urlpatterns = [
    path("thread/", views.thread),
    path("async/", views.async_scheduling),
    path("persist/", views.persistencia),
    path("get-agendamentos/", views.get_agendamentos),
]
