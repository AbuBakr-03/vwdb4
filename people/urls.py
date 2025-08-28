from django.urls import path
from . import views

app_name = 'people'

urlpatterns = [
    # Main directory (was contacts)
    path('', views.contact_list, name='contact_list'),  # Main directory
    
    # Contact management (keeping existing URLs for backward compatibility)
    path('contacts/', views.contact_list, name='contact_list_legacy'),
    path('contacts/create/', views.contact_create, name='contact_create'),
    path('contacts/<int:contact_id>/edit/', views.contact_edit, name='contact_edit'),
    path('contacts/<int:contact_id>/delete/', views.contact_delete, name='contact_delete'),
    path('contacts/import-csv/', views.contact_import_csv, name='contact_import_csv'),
    
    # Segment management
    path('segments/', views.segment_list, name='segment_list'),
    path('segments/create/', views.segment_create, name='segment_create'),
    
    # New navigation tabs
    path('roles/', views.placeholder_view, name='roles'),
]
