from django.urls import path
from account import views 

from django.contrib.auth import views as auth_views

urlpatterns = [
    path('register',views.register,name='register'),
    
    #email verification paths 
    
    path('email-verification/<str:uidb64>/<str:token>/',views.email_verification,name='email-verification'),
    
    path('email-verification-success/',views.email_verification_success,name='email-verification-success'),
    
    path('email-verification-sent/',views.email_verification_sent,name='email-verification-sent'),
    
    path('email-verification-failed/',views.email_verification_failed,name='email-verification-failed'),
    
    path('my-login/',views.my_login,name='my-login'),
    
    path('dashboard/',views.dashboard,name='dashboard'),
    
    path('profile-management/',views.profile_management,name='profile-management'),
    
    path('delete-account/',views.delete_account,name='delete-account'),
    
    path('user-logout/',views.user_logout,name='user-logout'),
    
    # password reset paths
    
    path('reset_password/',auth_views.PasswordResetView.as_view(template_name="account/password/password-reset.html"),name='reset_password'),
    
    path('reset_password_sent', auth_views.PasswordResetDoneView.as_view(template_name="account/password/password-reset-sent.html"), name='password_reset_done'),
    
    path('reset_password_complete/',auth_views.PasswordResetCompleteView.as_view(template_name="account/password/password-reset-complete.html"),name='password_reset_complete'),
    
    path('reset/<uidb64>/<token>/',auth_views.PasswordResetConfirmView.as_view(template_name="account/password/password-reset-form.html"),name='password_reset_confirm')    
      
]