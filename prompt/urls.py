from django.urls import path
from . import views

app_name = 'prompt'

urlpatterns = [
    path('', views.prompt_list, name='prompt_list'),
    path('playground/', views.agent_playground, name='agent_playground'),
    path('voices/', views.voices, name='voices'),
]
