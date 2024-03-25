from django.urls import path
from . import views

app_name = 'qgs_plugins'

urlpatterns = [
    path('', views.plugin_list, name='plugin_list'),
    path('download/<int:plugin_id>/', views.download_plugin, name='download_plugin'),
]
