from django.urls import path
from . import views

app_name = 'tools'

urlpatterns = [
    path('', views.tools_list, name='tools_list'),
    path('create/<str:tool_type>/', views.create_tool, name='create_tool'),
    path('<str:tool_id>/', views.tool_detail, name='tool_detail'),
    path('<str:tool_id>/save/', views.save_tool_config, name='save_tool_config'),
    path('<str:tool_id>/delete/', views.delete_tool, name='delete_tool'),
]
