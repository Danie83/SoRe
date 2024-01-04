from django import forms
from .models import *

class HobbiesForm(forms.Form):
    HOBBIES = (
        (1, 'Ski'),
        (2, 'Hiking'),
    )

    is_hidden = False
    name = 'hobbies-form'

    hobby1 = forms.ChoiceField(choices=HOBBIES, widget=forms.Select(attrs={'class': 'form-control my-3', 'id': 'hobby_choice1'}), required=False)
    hobby2 = forms.ChoiceField(choices=HOBBIES, widget=forms.Select(attrs={'class': 'form-control my-3', 'id': 'hobby_choice2'}), required=False)
    hobby3 = forms.ChoiceField(choices=HOBBIES, widget=forms.Select(attrs={'class': 'form-control my-3', 'id': 'hobby_choice3'}), required=False)

class SkillsForm(forms.Form):
    SKILLS = (
        (1, 'Programming'),
        (2, 'Singing'),
    )

    is_hidden = True
    name = 'skills-form'

    skill1 = forms.ChoiceField(choices=SKILLS, widget=forms.Select(attrs={'class': 'form-control my-3', 'id': 'skill_choice1'}), required=False)
    skill2 = forms.ChoiceField(choices=SKILLS, widget=forms.Select(attrs={'class': 'form-control my-3', 'id': 'skill_choice2'}), required=False)
    skill3 = forms.ChoiceField(choices=SKILLS, widget=forms.Select(attrs={'class': 'form-control my-3', 'id': 'skill_choice3'}), required=False)