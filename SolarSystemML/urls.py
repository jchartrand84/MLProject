from django.urls import path
from maintenance import views

urlpatterns = [
    path('', views.home, name='home'),  # Root URL maps to home view
    path('sensor_data/', views.sensor_data, name='sensor_data'),
    path('get_sensor_data/', views.get_sensor_data, name='get_sensor_data'),

    # Add the new paths for the additional pages
    path('controlpanel/', views.control_panel, name='control_panel'),
    path('log/', views.maintenance_log, name='maintenance_log'),
    path('acknowledge_warning/', views.acknowledge_warning, name='acknowledge_warning'),
    path('get_panel_data/', views.get_panel_data, name='get_panel_data'),
    path('readme/', views.view_readme, name='view_readme'),
]
