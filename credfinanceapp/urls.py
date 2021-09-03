from django.urls import path
from . import views

from rest_framework.authtoken.views import obtain_auth_token


urlpatterns = [
    path('', views.home_page, name='home_page'),
    path('signup/', views.sign_up_view, name="sign_up_view"),
    path('signin/', views.sign_in_view, name="sign_in_view"),
    path('signout/', views.sign_out_view, name="sign_out_view"),
    path('api/signin/', obtain_auth_token),
    path('api/register/', views.registration_api_endpoint),
    path('api/change-password/', views.change_password_api_endpoint),
]