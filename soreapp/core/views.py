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

from api.views import *
import requests

from SPARQLWrapper import SPARQLWrapper, JSON

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
        context = None
        try:
            current_profile = UserProfile.objects.get(user=request.user)
            # api_url = "http://localhost:8000/api/profile/"
            api_data, response_status = ProfileAPIView().get_profile_data(current_profile.user.username)

            if response_status == 200:
                context = convert_result_bindings(api_data)
            else:
                context = {'error': 'Failed to fetch data from the API'}

        except UserProfile.DoesNotExist:
            return redirect('login')
        return render(request, self.template_name, context)
    
def convert_result_bindings(results):
    template_context = dict()
    for result in results:
        property_uri = result["property"]
        property_name = result["tag"]
        property_value = result["value"]
        if property_name not in template_context.keys():
            template_context[property_name] = {
                'uri': property_uri,
                'value': property_value
            }
        else:
            if (isinstance(template_context[property_name]['value'], list)):
                template_context[property_name]['value'].append(property_value)
                continue
            tmp = template_context[property_name]['value']
            template_context[property_name]['value'] = list()
            template_context[property_name]['value'].append(property_value)
    return { 'context': template_context }

class ProfileUpdateView(LoginRequiredMixin, View):
    template_name = 'profile_form.html'
    login_url = 'login/'

    def get(self, request):
        basic_form = BasicProfileForm()
        moderate_form = ModerateProfileForm()
        advanced_form = AdvancedProfileForm()
        activity_form = ActivityProfileForm()
        description_form = DescriptionProfileForm()

        forms = list()
        forms.append(basic_form)
        forms.append(moderate_form)
        forms.append(advanced_form)
        forms.append(activity_form)
        forms.append(description_form)
        context = {
            'forms': forms
        }
        return render(request, self.template_name, context)

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
            try:
                current_profile = UserProfile.objects.get(user=user)
                if current_profile.setup_complete:
                    return redirect('presentation')
            except UserProfile.DoesNotExist:
                return redirect(self.login_url)
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
            return redirect('presentation')
        return render(request, self.template_name, {'form': form})

class UserLogoutView(LogoutView):
    next_page = reverse_lazy('login')

class SetupView(LoginRequiredMixin, View):
    template_name = 'setup.html'
    login_url = 'login/'

    def get(self, request, *args, **kwargs):
        basic_form = BasicProfileForm()
        moderate_form = ModerateProfileForm()
        advanced_form = AdvancedProfileForm()
        activity_form = ActivityProfileForm()
        description_form = DescriptionProfileForm()

        forms = list()
        forms.append(basic_form)
        forms.append(moderate_form)
        forms.append(advanced_form)
        forms.append(activity_form)
        forms.append(description_form)
        context = {
            'forms': forms
        }
        return render(request, self.template_name, context)
    
def submit_form(request):
    try:
        current_profile = UserProfile.objects.get(user=request.user)
        current_profile.setup_complete = True
        current_profile.save()
    except UserProfile.DoesNotExist:
        return redirect('login')
    return JsonResponse({'success': True}, status=200)