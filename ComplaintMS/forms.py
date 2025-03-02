# forms.py
from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from .models import Profile, Complaint
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit

class ComplaintForm(forms.ModelForm):
    class Meta:
        model = Complaint
        fields = ('Subject', 'Type_of_complaint', 'Description')

    def __init__(self, *args, **kwargs):
        super(ComplaintForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.add_input(Submit('submit', 'Submit'))


class UserProfileform(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ('collegename', 'contactnumber', 'Branch')


class UserRegisterForm(UserCreationForm):
    first_name = forms.CharField(max_length=30, required=True)
    last_name = forms.CharField(max_length=30, required=True)

    class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name', 'email', 'password1', 'password2')

    def clean_email(self):
        email = self.cleaned_data.get('email')

        # Check to see if any users already exist with this email
        try:
            match = User.objects.get(email=email)
        except User.DoesNotExist:
            return email

        raise forms.ValidationError('This email address is already in use.')


class ProfileUpdateForm(forms.ModelForm):
    email = forms.EmailField(widget=forms.TextInput(attrs={'readonly': 'readonly'}))
    first_name = forms.CharField(max_length=30, required=True)
    last_name = forms.CharField(max_length=30, required=True)

    class Meta:
        model = User
        fields = ['username', 'email', 'first_name', 'last_name']

    def clean_email(self):
        email = self.cleaned_data.get('email')

        try:
            match = User.objects.exclude(pk=self.instance.pk).get(email=email)
        except User.DoesNotExist:
            return email

        raise forms.ValidationError('This email address is already in use.')


class UserProfileUpdateform(forms.ModelForm):
    collegename = forms.CharField(widget=forms.TextInput(attrs={'readonly': 'readonly'}))
    Branch = forms.CharField(widget=forms.TextInput(attrs={'readonly': 'readonly'}))

    class Meta:
        model = Profile
        fields = ('collegename', 'contactnumber', 'Branch')


class StatusUpdateForm(forms.ModelForm):
    class Meta:
        model = Complaint
        fields = ('status',)
        help_texts = {
            'status': None,
        }
