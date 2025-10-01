from django.urls import path
from . import web_views


urlpatterns = [
    path('register/', web_views.register_view, name='register'),
    path('login/', web_views.login_view, name='login'),
    path('logout/', web_views.logout_view, name='logout'),
    path('profile/', web_views.profile_view, name='profile'),
]


