from django.urls import path
from .views import *

urlpatterns=[
    path('', IndexView.as_view(), name='index'),
    path('google-login/', GoogleLoginView.as_view(), name='google_login'),
    path('google-callback/', GoogleCallbackView.as_view(), name='google_callback'),
]