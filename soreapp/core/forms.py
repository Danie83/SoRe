from django import forms
from .models import *

class BasicProfileForm(forms.Form):
    GENDERS = (
        (1, 'Male'),
        (2, 'Female'),
        (3, 'Other')
    )

    is_hidden = False
    name = 'basic-profile-form'

    first_name = forms.CharField(label='First Name', widget=forms.TextInput(attrs={'class': 'form-control my-3', 'id': 'first_name_field'}), required=False)
    last_name = forms.CharField(label='Last Name', widget=forms.TextInput(attrs={'class': 'form-control my-3', 'id': 'last_name_field'}), required=False)
    gender = forms.ChoiceField(label="Gender", choices=GENDERS, initial=GENDERS[-1][0], widget=forms.Select(attrs={'class': 'form-control my-3', 'id': 'skill_choice'}), required=False)
    nickname = forms.CharField(label='Nickname', widget=forms.TextInput(attrs={'class': 'form-control my-3', 'id': 'nickname_field'}), required=False)
    birth_date = forms.DateTimeField(label="Birth Date", input_formats=['%d/%m/%Y'], widget=forms.DateTimeInput(attrs={'class': 'form-control my-3 datetimepicker-input','data-target': '#datetimepicker1', 'id': 'birth_date'}), required=False)

class ModerateProfileForm(forms.Form):

    RELATIONSHIP_STATUSES = (
        (1, 'Single'),
        (2, 'In a relationship'),
        (3, 'Married'),
        (4, 'Other')
    )

    is_hidden = True
    name = 'moderate-profile-form'
        
    country = forms.CharField(label='Country', widget=forms.TextInput(attrs={'class': 'form-control my-3', 'id': 'country_field'}), required=False)
    state = forms.CharField(label='State', widget=forms.TextInput(attrs={'class': 'form-control my-3', 'id': 'state_field'}), required=False)
    highschool = forms.CharField(label='Highschool', widget=forms.TextInput(attrs={'class': 'form-control my-3', 'id': 'highschool_field'}), required=False)
    college = forms.CharField(label='College', widget=forms.TextInput(attrs={'class': 'form-control my-3', 'id': 'college_field'}), required=False)
    relationship_status = forms.ChoiceField(label='Relationship Status', choices=RELATIONSHIP_STATUSES, initial=RELATIONSHIP_STATUSES[-1][0], widget=forms.Select(attrs={'class': 'form-control my-3', 'id': 'relationship_status_choice'}), required=False)

class AdvancedProfileForm(forms.Form):
    is_hidden = True
    name = 'advanced-profile-form'

    job = forms.CharField(label='Job', widget=forms.TextInput(attrs={'class': 'form-control my-3', 'id': 'job_field'}), required=False)
    email = forms.EmailField(label='Email', widget=forms.EmailInput(attrs={'class': 'form-control my-3', 'id': 'email_field'}), required=False)
    company = forms.CharField(label='Company', widget=forms.TextInput(attrs={'class': 'form-control my-3', 'id': 'company_field'}), required=False)
    webiste = forms.CharField(label='Personal Website', widget=forms.TextInput(attrs={'class': 'form-control my-3', 'id': 'website_field'}), required=False)

class ActivityProfileForm(forms.Form):
    HOBBIES = (
        (1, 'Ski'),
        (2, 'Hiking'),
        (3, 'Other')
    )

    SKILLS = (
        (1, 'Programming'),
        (2, 'Singing'),
        (3, 'Other')
    )

    FEELINGS = (
        (1, 'Happy'),
        (2, 'Sad'),
        (3, 'Other')
    )

    is_hidden = True
    name = 'activity-profile-form'

    hobby1 = forms.ChoiceField(label="Hobby", choices=HOBBIES, initial=HOBBIES[-1][0], widget=forms.Select(attrs={'class': 'form-control my-3', 'id': 'hobby_choice'}), required=False)
    skill1 = forms.ChoiceField(label="Skill", choices=SKILLS, initial=SKILLS[-1][0], widget=forms.Select(attrs={'class': 'form-control my-3', 'id': 'skill_choice'}), required=False)
    feeling = forms.ChoiceField(label="How are you feeling today?", choices=FEELINGS, initial=FEELINGS[-1][0], widget=forms.Select(attrs={'class': 'form-control my-3', 'id': 'emotion_choice'}), required=False)
    
class DescriptionProfileForm(forms.Form):
    is_hidden = True
    name = 'description-profile-form'

    description = forms.CharField(label="Write something about yourself", widget=forms.Textarea(attrs={'class': 'form-control my-3', 'id': 'description_field'}), required=False)
