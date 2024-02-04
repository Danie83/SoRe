from django.urls import path
from .views import *

urlpatterns=[
    path('', PresentationView.as_view(), name='presentation'),
    path('login/', UserLoginView.as_view(), name='login'),
    path('register/', UserRegistrationView.as_view(), name='register'),
    path('setup/', SetupView.as_view(), name='setup'),
    path('ajax/post/submit-form', submit_form, name='submit_form'),
    path('ajax/post/submit-profile-update-form', submit_profile_update_form, name='submit_profile_update_form'),
    path('logout/', UserLogoutView.as_view(), name='logout'),
    path('google-login/', GoogleLoginView.as_view(), name='google_login'),
    path('google-callback/', GoogleCallbackView.as_view(), name='google_callback'),
    path('explore/', ExploreView.as_view(), name='explore'),
    path('history/', HistoryView.as_view(), name='history'),
    path('profile/', ProfileView.as_view(), name='profile'),
    path('profile/update/', ProfileUpdateView.as_view(), name='profile_update'),
]