from django.contrib import messages
from django.contrib.auth import authenticate, login
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import  LogoutView
from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from django.views import View
from django.http import JsonResponse

from utils import googleoauth
from .forms import *

# Create your views here.

class PresentationView(View):
    template_name = 'presentation.html'

    def get(self, request):
        return render(request, self.template_name)

class ExploreView(LoginRequiredMixin, View):
    template_name = 'explore.html'
    login_url = 'login/'

    def get(self, request):
        return render(request, self.template_name)

class HistoryView(LoginRequiredMixin, View):
    template_name = 'history.html'
    login_url = 'login/'

    def get(self, request):
        return render(request, self.template_name)

class ProfileView(LoginRequiredMixin, View):
    template_name = 'profile.html'
    login_url = 'login/'

    def get(self, request):
        return render(request, self.template_name)

class GoogleLoginView(View):
    def post(self, request):
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
        
class UserLoginView(View):
    template_name = 'login.html'

    def get(self, request, *args, **kwargs):
        form = AuthenticationForm()
        return render(request, self.template_name, {'form': form})

    def post(self, request, *args, **kwargs):
        form = AuthenticationForm(data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect('setup')
        return render(request, self.template_name, {'form': form})

class UserRegistrationView(View):
    template_name = 'register.html'

    def get(self, request, *args, **kwargs):
        form = UserCreationForm()
        return render(request, self.template_name, {'form': form})

    def post(self, request, *args, **kwargs):
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('index')
        return render(request, self.template_name, {'form': form})

class UserLogoutView(LogoutView):
    next_page = reverse_lazy('login')

class SetupView(LoginRequiredMixin, View):
    template_name = 'setup.html'
    login_url = 'login/'

    def get(self, request, *args, **kwargs):
        hobbies_form = HobbiesForm()
        skills_form = SkillsForm()

        forms = list()
        forms.append(hobbies_form)
        forms.append(skills_form)
        return render(request, self.template_name, {'forms': forms})
    
def submit_form(request):
    return JsonResponse({'success': True}, status=200)