from django.urls import path
from .views import flights_views

urlpatterns = [
    path('dashboard/flights/', flights_views.flights, name='flights_page'),
    path('dashboard/flights/data_tables/', flights_views.data_tables, name='flights_datatable'),
    path('dashboard/flights/info/', flights_views.flight_info, name='flight_info'),
    path('dashboard/flights/create/', flights_views.create_flight, name='create_flight'),
    path('dashboard/flights/crews/', flights_views.get_crews, name='get_crews'),
    path('dashboard/flights/update_crews/', flights_views.update_crews, name='update_crews'),
    path('dashboard/flights/get_filters/', flights_views.get_filters, name='get_filters'),
    path('dashboard/flights/delete/', flights_views.flight_delete, name='delete_flight'),
]
