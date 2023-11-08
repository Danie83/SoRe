from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.views import View
from utils import googleoauth
import requests
import json

# Create your views here.

class IndexView(View):
    def get(self, request):
        return render(request, 'index.html')

class GoogleLoginView(View):
    def get(self, request):
        auth_url = googleoauth.create_auth_url()
        return redirect(auth_url)

class GoogleCallbackView(View):
    def get(self, request):
        code = self.request.GET.get('code')
        if code:
            data = googleoauth.authorize()
            return HttpResponse("Authentication successful")
        else:
            return HttpResponse("Authentication failed")