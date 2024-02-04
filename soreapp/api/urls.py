from django.urls import path
from .views import *

urlpatterns = [
    path('profile/', ProfileAPIView.as_view(), name='profile_api'),
    path('profiles/', ProfilesAPIView.as_view(), name='profiles_api'),
    path('ratings/', RateAPIView.as_view(), name='profile_ratings_api'),
    path('recommendations/', RecommenderAPIView.as_view(), name='profile_recommendations_api')
]