"""
Campaigns module URL configuration.
"""

from django.urls import path
from . import views

app_name = 'campaigns'

urlpatterns = [
    # Campaign management
    path('', views.CampaignListView.as_view(), name='campaign_list'),
    path('create/', views.CampaignCreateView.as_view(), name='campaign_create'),
    path('<int:campaign_id>/', views.CampaignDetailView.as_view(), name='campaign_detail'),
    path('<int:campaign_id>/edit/', views.CampaignEditView.as_view(), name='campaign_edit'),
    path('<int:campaign_id>/launch/', views.CampaignLaunchView.as_view(), name='campaign_launch'),
    
    # Queue and sessions
    path('queue/', views.QueueTrackerView.as_view(), name='queue_tracker'),
    path('sessions/', views.SessionsView.as_view(), name='sessions'),
    
    # API endpoints
    path('api/stats/', views.campaign_stats_api, name='campaign_stats_api'),
    path('api/queue-status/', views.queue_status_api, name='queue_status_api'),
]
