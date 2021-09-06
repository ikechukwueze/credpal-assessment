from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

#from rest_framework.authtoken.views import obtain_auth_token


urlpatterns = [
    path('', views.home_page, name='home_page'),
    path('signup/', views.sign_up_view, name="sign_up_view"),
    path('signin/', views.sign_in_view, name="sign_in_view"),
    path('signout/', views.sign_out_view, name="sign_out_view"),

    path('reset_password/', auth_views.PasswordResetView.as_view(template_name='credfinanceapp/password-reset.html'), name="reset_password"),
    path('reset_password_sent/', auth_views.PasswordResetDoneView.as_view(template_name='credfinanceapp/password-reset-sent.html'), name="password_reset_done"),
    path('reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(template_name='credfinanceapp/password-reset-confirm.html'), name="password_reset_confirm"),
    path('reset_password_complete/', auth_views.PasswordResetCompleteView.as_view(template_name='credfinanceapp/password-reset-complete.html'), name="password_reset_complete"),

    #path('api/signin/', obtain_auth_token),
    #path('api/register/', views.registration_api_endpoint),
    path('api/signin/', views.SignInView.as_view(), name='sign_in_api_view'),
    path('api/register/', views.RegistrationView.as_view(), name='sign_up_api_view'),
    path('api/change-password/', views.ChangePasswordView.as_view(), name='change_password'),
    path('api/userprofile/<str:email>/', views.RetrieveUpdateProfileView.as_view(), name='userprofile'),
    path('api/walletbalance/<int:pk>/', views.RetrieveWalletBalanceView.as_view(), name='walletbalance'),
    path('api/transferfunds/', views.TransferFundsView.as_view(), name='transferfunds'),
    path('api/request-password-reset/', views.RequestPasswordResetEmailView.as_view(), name='api-request-password-reset'),
    path('api/password-reset/<uidb64>/<token>/', views.PasswordTokenCheckView.as_view(), name='api-password-reset'),
    path('api/password-reset-done/', views.ResetPasswordView.as_view(), name='api-password-reset-done'),
]