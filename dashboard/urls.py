from django.urls import path
from . import views

app_name = 'dashboard'

urlpatterns = [
    path("", views.overview, name="index"),
    path("home/", views.home, name="home"),
    path("overview/", views.overview, name="overview"),
    path("assistants/", views.AssistantsView.as_view(), name="assistants"),
    path("assistants/create/", views.CreateAssistantView.as_view(), name="create_assistant"),
    path("assistants/<uuid:assistant_id>/", views.AssistantDetailView.as_view(), name="assistant_detail"),
    path("assistants/<uuid:assistant_id>/save/", views.SaveAssistantConfigView.as_view(), name="save_assistant_config"),
    path("phone-numbers/", views.phone_numbers, name="phone_numbers"),
    path("voice-library/", views.voice_library, name="voice_library"),
    path("api-keys/", views.api_keys, name="api_keys"),
    path("api-keys/save/", views.save_api_keys, name="save_api_keys"),
]
