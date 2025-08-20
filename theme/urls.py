from django.urls import path
import theme.views as views

urlpatterns = [
    path('', views.home, name="home_page"),
    path('blogs/', views.blogs, name="blogs_page"),
    path('blogs/<int:pid>/', views.blog, name="blog_page"),
    path('about/', views.about, name="about_page"),
    path('contact/', views.contact, name="contact_page"),
]
