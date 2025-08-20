from django.urls import path
from .views import admin_views, crew_views

urlpatterns = [
    path('dashboard/admins/', admin_views.admins, name='admins_page'),
    path('dashboard/crews/', crew_views.crews, name='crews_page'),
    path('dashboard/admins/data/', admin_views.admin_data, name='admin_data'),
    path('dashboard/admins/create/', admin_views.create_admin, name='create_admin'),
    path('dashboard/admins/update/', admin_views.update_admin, name='update_admin'),
    path('dashboard/admins/delete/', admin_views.delete_admin, name='delete_admin'),
    path('dashboard/admins/details/', admin_views.get_admin_details, name='get_admin_details'),
    
    # Crew URLs
    path('dashboard/crews/data/', crew_views.crew_data, name='crew_data'),
    path('dashboard/crews/create/', crew_views.create_crew, name='create_crew'),
    path('dashboard/crews/update/', crew_views.update_crew, name='update_crew'),
    path('dashboard/crews/delete/', crew_views.delete_crew, name='delete_crew'),
    path('dashboard/crews/details/', crew_views.get_crew_details, name='get_crew_details'),
]
