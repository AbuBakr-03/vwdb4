from django.urls import path
from . import views

app_name = 'tickets'

urlpatterns = [
    # Dashboard
    path('', views.dashboard, name='dashboard'),
    
    # Ticket management
    path('tickets/', views.TicketListView.as_view(), name='ticket_list'),
    path('tickets/create/', views.TicketCreateView.as_view(), name='ticket_create'),
    path('tickets/<uuid:pk>/', views.TicketDetailView.as_view(), name='ticket_detail'),
    path('tickets/<uuid:pk>/edit/', views.TicketUpdateView.as_view(), name='ticket_update'),
    
    # Ticket actions
    path('tickets/<uuid:ticket_id>/comment/', views.add_comment, name='add_comment'),
    path('tickets/<uuid:ticket_id>/attachment/', views.add_attachment, name='add_attachment'),
    path('tickets/<uuid:ticket_id>/status/', views.update_ticket_status, name='update_ticket_status'),
    path('tickets/<uuid:ticket_id>/assign/', views.assign_ticket, name='assign_ticket'),
    
    # Company management (staff only)
    path('companies/', views.CompanyListView.as_view(), name='company_list'),
    path('companies/create/', views.CompanyCreateView.as_view(), name='company_create'),
    path('companies/<int:pk>/edit/', views.CompanyUpdateView.as_view(), name='company_update'),
    
    # QA Tester management (staff only)
    path('qa-testers/', views.QATesterListView.as_view(), name='qa_tester_list'),
    path('qa-testers/create/', views.QATesterCreateView.as_view(), name='qa_tester_create'),
]




