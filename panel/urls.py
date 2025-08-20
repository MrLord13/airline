from django.urls import path
from panel.views import dashboard, login_view, logout_view, profile, update_profile
from . import views

urlpatterns = [
    ### Auth ###
    path('login/', login_view, name="login_page"),

    ### Dashboard ###
    path('dashboard/', dashboard, name="dashboard"),
    path('dashboard/profile/', profile, name='profile'),
    path('dashboard/profile/update/', update_profile, name='update_profile'),
    path('logout/', logout_view, name="logout_page"),
]
