from django import forms
# from django.contrib.auth.forms import UserCreationForm
from django.core.validators import RegexValidator
from django.contrib.auth.models import User

# from django.contrib.auth.models import User
from django import forms
from django.core.validators import RegexValidator

class SignUpForm(forms.Form):
    first_name = forms.CharField(label='First Name', max_length=100)
    last_name = forms.CharField(label='Last Name', max_length=100)
    email = forms.EmailField(label='Email address')
    password = forms.CharField(widget=forms.PasswordInput(), label='Password')
    confirm_password = forms.CharField(widget=forms.PasswordInput(), label='Confirm Password')

    
class LoginForm(forms.Form):
    email = forms.EmailField(label='Email address')
    password = forms.CharField(widget=forms.PasswordInput(), label='Password')

    def clean(self):
        super(LoginForm, self).clean()
        email = self.cleaned_data.get('email')
        password = self.cleaned_data.get('password')

        # Custom validation for email length
        if len(email) < 5:
            self._errors['email'] = self.error_class([
                'Minimum 5 characters required for email'])

        # Custom validation for password length
        if len(password) < 8:
            self._errors['password'] = self.error_class([
                'Password must be at least 8 characters long'])

        return self.cleaned_data
    

# forms.py
from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm

class RegistrationForm(UserCreationForm):
    email = forms.EmailField(required=True)

    class Meta:
        model = User
        fields = ("username", "first_name", "last_name","email","password1", "password2")
    
    def save(self, commit=True):
        user = super(RegistrationForm, self).save(commit=False)
        user.email = self.cleaned_data['email']
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']
        if commit:
            user.save()
        return user
