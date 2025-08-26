from django.urls import path
from . import views

app_name = 'accounts'

urlpatterns = [
    path('login/', views.login_view, name='login'),
    path('register/', views.register_view, name='register'),
    path('logout/', views.logout_view, name='logout'),
    path('access-denied/', views.access_denied_view, name='access_denied'),
    
    # User Management (Root Users Only)
    path('users/', views.company_users, name='company_users'),
    path('users/create/', views.create_sub_user, name='create_sub_user'),
    
    # Test view for the new data table component
    path('users/data-table-test/', views.company_users_data_table_test, name='company_users_data_table_test'),
    
    # Simple test view

]
