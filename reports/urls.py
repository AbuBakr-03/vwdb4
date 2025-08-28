from django.urls import path
from . import views

app_name = 'reports'

urlpatterns = [
    path('', views.reports_overview, name='reports_overview'),
    path('exports/', views.exports, name='exports'),
]
