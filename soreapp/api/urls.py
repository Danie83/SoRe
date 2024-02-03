from django.urls import path
from .views import *

urlpatterns = [
    path('profile/', ProfileAPIView.as_view(), name='profile_api'),
    path('profiles/', ProfilesAPIView.as_view(), name='profiles_api'),
]