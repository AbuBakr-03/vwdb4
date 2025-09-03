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
    
    # Knowledge Base URLs
    path("assistants/<uuid:assistant_id>/upload-file/", views.upload_file, name="upload_file"),
    path("assistants/<uuid:assistant_id>/delete-file/<uuid:file_id>/", views.delete_file, name="delete_file"),
    path("assistants/<uuid:assistant_id>/add-website/", views.add_website, name="add_website"),
    path("assistants/<uuid:assistant_id>/delete-website/<int:website_id>/", views.delete_website, name="delete_website"),
    path("assistants/<uuid:assistant_id>/knowledge-base/", views.get_knowledge_base, name="get_knowledge_base"),
    
    # Metrics URL
    path("metrics/", views.metrics, name="metrics"),
]
