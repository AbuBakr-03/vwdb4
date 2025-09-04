"""
Campaigns module URL configuration.
"""

from django.urls import path
from . import views

app_name = 'campaigns'

urlpatterns = [
    # Enhanced dashboard and monitoring
    path('', views.CampaignDashboardView.as_view(), name='dashboard'),
    path('list/', views.CampaignListView.as_view(), name='campaign_list'),
    path('queue/', views.CampaignQueueView.as_view(), name='queue_monitor'),
    
    # Campaign management
    path('create/', views.CampaignCreateView.as_view(), name='campaign_create'),
    path('<int:campaign_id>/', views.CampaignDetailView.as_view(), name='campaign_detail'),
    path('<int:campaign_id>/edit/', views.CampaignEditView.as_view(), name='campaign_edit'),
    
    # Campaign actions
    path('<int:campaign_id>/action/', views.CampaignActionView.as_view(), name='campaign_action'),
    
    # Legacy URLs for backward compatibility
    path('campaigns/', views.CampaignListView.as_view(), name='campaigns_list'),
    path('campaign/<int:campaign_id>/', views.CampaignDetailView.as_view(), name='campaign_detail_legacy'),
    
    # API endpoints
    path('api/launch/<int:campaign_id>/', views.CampaignLaunchView.as_view(), name='campaign_launch'),
    path('api/queue-status/', views.QueueStatusView.as_view(), name='queue_status'),
]
