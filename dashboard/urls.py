from django.urls import path
from . import views

app_name = 'dashboard'

urlpatterns = [
    path("", views.overview, name="index"),
    path("home/", views.home, name="home"),
    path("overview/", views.overview, name="overview"),
    path("assistants/", views.assistants, name="assistants"),
]
