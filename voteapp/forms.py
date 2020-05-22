from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User


class SignUpForm(UserCreationForm):
    email = forms.EmailField(max_length=254, help_text='Required. Inform a valid email address.')

    class Meta:
        model = User
        fields = ('username', 'email', 'password1', 'password2',)


class AddVotingForm(forms.Form):
    name = forms.CharField(label='Name of your voting', max_length=50)
    text = forms.CharField(label='Your text', max_length=400)
    check = forms.BooleanField(label="Checkbox type", required=False)


class OptionTextForm(forms.Form):
    text = forms.CharField(label="", max_length=400, widget=forms.TextInput(attrs={'placeholder': 'New option'}))


class AuthForm(forms.Form):
    username = forms.CharField(label='User')
    password = forms.CharField(label='Password', widget=forms.PasswordInput())


class SearchForm(forms.Form):
    check = forms.CharField(label="Search", max_length=100)


class RecoverForm(forms.Form):
    username = forms.CharField(label='User')


class ImageForm(forms.Form):
    img = forms.ImageField(label='Avatar')


class CommentForm(forms.Form):
    text = forms.CharField(label="Your comment", max_length=400)
