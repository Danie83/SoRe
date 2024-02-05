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
from datetime import datetime

from django.core.cache import cache

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
        api_data, response_status = RecommenderAPIView().get_recommendations(request.user.username)
        if response_status == 200:
            context = convert_explore_results(api_data, request.user.username)
        else:
            context = {'error': 'Failed to fetch data from the API'}
        return render(request, self.template_name, { 'profiles': context})
    
def convert_explore_results(data, username):
    import random
    context = list()
    for result in data:
        current_data = convert_result_bindings(result['data'])
        context.append(current_data)
    random.shuffle(context)
    return context

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
            template_context[property_name]['value'].append(tmp)
    if 'WebSite' in template_context.keys() and not isinstance(template_context['WebSite'], list):
        tmp = template_context['WebSite']['value']
        template_context['WebSite']['value'] = list()
        template_context['WebSite']['value'].append(tmp)
    if 'skills' in template_context.keys() and not isinstance(template_context['skills'], list):
        tmp = template_context['skills']['value']
        template_context['skills']['value'] = list()
        template_context['skills']['value'].append(tmp)
    if 'Hobby' in template_context.keys() and not isinstance(template_context['Hobby'], list):
        tmp = template_context['Hobby']['value']
        template_context['Hobby']['value'] = list()
        template_context['Hobby']['value'].append(tmp)
    if 'alumniOf' in template_context.keys() and not isinstance(template_context['alumniOf'], list):
        tmp = template_context['alumniOf']['value']
        template_context['alumniOf']['value'] = list()
        template_context['alumniOf']['value'].append(tmp)
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
            return redirect('setup')
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
    current_profile = UserProfile.objects.get(user=request.user)

    user_data = cache.get(current_profile.user.username)

    if request.method == "POST":
        form_type = request.POST.get('form_type')
        if form_type == "basic-profile-form":
            first_name = request.POST.get('first_name')
            last_name = request.POST.get('last_name')
            full_name = request.POST.get('full_name')
            gender = int(request.POST.get('gender'))
            nickname = request.POST.get('nickname')
            birth_date = request.POST.get('birth_date')

            if user_data is None:
                user_data = dict()
            if len(first_name) > 0:
                user_data['firstName'] = first_name
            if len(last_name) > 0:
                user_data['lastName'] = last_name
            if len(full_name) > 0:
                user_data['name'] = full_name
            if gender != 3:
                cgender = next((cgender for value, cgender in BasicProfileForm.GENDERS if value == gender), None)
                if cgender is not None:
                    user_data['gender'] = cgender
            
            user_data['accountName'] = current_profile.user.username
            if len(birth_date) > 0:
                user_data['birthdate'] = datetime.strptime(birth_date, '%d/%m/%Y').strftime('%Y-%m-%dT')
            cache.set(current_profile.user.username, user_data)
        elif form_type == "moderate-profile-form":
            country = request.POST.get('country')
            state = request.POST.get('state')
            highschool = request.POST.get('highschool')
            college = request.POST.get('college')
            relationship_status = int(request.POST.get('relationship_status'))

            if user_data is None:
                user_data = dict()
            if len(country) > 0:
                user_data['Country'] = country
            if len(highschool) > 0 or len(college) > 0:
                user_data['alumniOf'] = list()
                if len(highschool) > 0:
                    user_data['alumniOf'].append(highschool)
                if len(college) > 0:
                    user_data['alumniOf'].append(college)
            if relationship_status != 4:
                relationship_status1 = next((rs for value, rs in ModerateProfileForm.RELATIONSHIP_STATUSES if value == relationship_status), None)
                if relationship_status1 is not None:
                    user_data['MarryAction'] = relationship_status
            cache.set(current_profile.user.username, user_data)
        elif form_type == "advanced-profile-form":
            job = request.POST.get('job')
            email = request.POST.get('email')
            company = request.POST.get('company')
            job = request.POST.get('job')
            website = request.POST.get('website')

            if user_data is None:
                user_data = dict()
            
            if len(job) > 0:
                user_data['Occupation'] = job
            if len(company) > 0:
                user_data['Organization'] = company
            if len(email) > 0:
                user_data['email'] = email
            if len(website):
                user_data['WebSite'] = website
            cache.set(current_profile.user.username, user_data)
        elif form_type == "activity-profile-form":
            hobby = int(request.POST.get('hobby1'))
            skill = int(request.POST.get('skill1'))
            feeling = int(request.POST.get('feeling'))

            if user_data is None:
                user_data = dict()
            h = next((h1 for value, h1 in ActivityProfileForm.HOBBIES if value == hobby), None)
            if h is not None and h != "Other":
                user_data['Hobby'] = list()
                user_data['Hobby'].append(h)
            s = next((s1 for value, s1 in ActivityProfileForm.SKILLS if value == skill), None)
            if s is not None and s != 'Other':
                user_data['skills'] = list()
                user_data['skills'].append(s)
            f = next((f1 for value, f1 in ActivityProfileForm.FEELINGS if value == feeling), None)
            if f is not None and f != "Other":
                user_data['status'] = f
            cache.set(current_profile.user.username, user_data)
        elif form_type == "description-profile-form":
            description = request.POST.get('description')

            if user_data is None:
                user_data = dict()
            if len(description) > 0:
                user_data['description'] = description
            api_data, response_status = ProfileAPIView().create_profile(current_profile.user.username, user_data)

            cache.delete(current_profile.user.username)

            current_profile.setup_complete = True
            current_profile.save()
            return JsonResponse({'success': True}, status=200)
        else:
            return JsonResponse({'success': False}, status=404)
    else:
        return JsonResponse({'success': False}, status=405)
    return JsonResponse({'success': True}, status=200)

def submit_profile_update_form(request):
    current_profile = UserProfile.objects.get(user=request.user)
    user_data = dict()
    if request.method == "POST":
        form_type = request.POST.get('form_type')
        if form_type == "basic-profile-form":
            has_data = False
            first_name = request.POST.get('first_name')
            last_name = request.POST.get('last_name')
            full_name = request.POST.get('full_name')
            gender = int(request.POST.get('gender'))
            nickname = request.POST.get('nickname')
            birth_date = request.POST.get('birth_date')

            if len(first_name) > 0:
                user_data['firstName'] = first_name
                has_data = True
            if len(last_name) > 0:
                user_data['lastName'] = last_name
                has_data = True
            if len(full_name) > 0:
                user_data['name'] = full_name
                has_data = True
            if gender != 3:
                cgender = next((cgender for value, cgender in BasicProfileForm.GENDERS if value == gender), None)
                if cgender is not None:
                    user_data['gender'] = cgender
                    has_data = True
            
            if len(birth_date) > 0:
                user_data['birthdate'] = datetime.strptime(birth_date, '%d/%m/%Y').strftime('%Y-%m-%dT')
                has_data = True

            if has_data:
                api_data, response_status = ProfileAPIView().update_profile(current_profile.user.username, user_data)
            return JsonResponse({'success': True}, status=200)
        elif form_type == "moderate-profile-form":
            has_data = False
            country = request.POST.get('country')
            state = request.POST.get('state')
            highschool = request.POST.get('highschool')
            college = request.POST.get('college')
            relationship_status = int(request.POST.get('relationship_status'))

            if len(country) > 0:
                user_data['Country'] = country
                has_data = True
            if len(highschool) > 0 or len(college) > 0:
                user_data['alumniOf'] = list()
                if len(highschool) > 0:
                    user_data['alumniOf'].append(highschool)
                if len(college) > 0:
                    user_data['alumniOf'].append(college)
                has_data = True
            if relationship_status != 4:
                relationship_status1 = next((rs for value, rs in ModerateProfileForm.RELATIONSHIP_STATUSES if value == relationship_status), None)
                if relationship_status1 is not None:
                    user_data['MarryAction'] = relationship_status
                    has_data = True
            if has_data:
                api_data, response_status = ProfileAPIView().update_profile(current_profile.user.username, user_data)
            return JsonResponse({'success': True}, status=200)
        elif form_type == "advanced-profile-form":
            has_data = False
            job = request.POST.get('job')
            email = request.POST.get('email')
            company = request.POST.get('company')
            job = request.POST.get('job')
            website = request.POST.get('website')

            if len(job) > 0:
                user_data['Occupation'] = job
                has_data = True
            if len(company) > 0:
                user_data['Organization'] = company
                has_data = True
            if len(email) > 0:
                user_data['email'] = email
                has_data = True
            if len(website):
                user_data['WebSite'] = website
                has_data = True

            if has_data:
                api_data, response_status = ProfileAPIView().update_profile(current_profile.user.username, user_data)
            return JsonResponse({'success': True}, status=200)
        elif form_type == "activity-profile-form":
            has_data = False
            hobby = int(request.POST.get('hobby1'))
            skill = int(request.POST.get('skill1'))
            feeling = int(request.POST.get('feeling'))

            h = next((h1 for value, h1 in ActivityProfileForm.HOBBIES if value == hobby), None)
            if h is not None and h != "Other":
                user_data['Hobby'] = list()
                user_data['Hobby'].append(h)
                has_data = True
            s = next((s1 for value, s1 in ActivityProfileForm.SKILLS if value == skill), None)
            if s is not None and s != 'Other':
                user_data['skills'] = list()
                user_data['skills'].append(s)
                has_data = True
            f = next((f1 for value, f1 in ActivityProfileForm.FEELINGS if value == feeling), None)
            if f is not None and f != "Other":
                user_data['status'] = f
                has_data = True

            if has_data:
                api_data, response_status = ProfileAPIView().update_profile(current_profile.user.username, user_data)
            return JsonResponse({'success': True}, status=200)
        elif form_type == "description-profile-form":
            has_data = False
            description = request.POST.get('description')

            if len(description) > 0:
                user_data['description'] = description
                has_data = True
            
            if has_data:
                api_data, response_status = ProfileAPIView().update_profile(current_profile.user.username, user_data)

            return JsonResponse({'success': True}, status=200)
        else:
            return JsonResponse({'success': False}, status=404)
    else:
        return JsonResponse({'success': False}, status=405)

def rate_profiles(request):
    if request.method == "GET":
        account = request.GET.get('account')
        like = True if request.GET.get('like') == "true" else False
        api_data, response_status = RateAPIView().rate_profile(request.user.username, like, account)
        return JsonResponse({'success': True}, status=200)
    else:
        return JsonResponse({'success': False}, status=405)