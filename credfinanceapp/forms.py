from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import Account



class SignUpForm(UserCreationForm):
    first_name = forms.CharField(
        min_length=2,
        max_length=30,
        required=True,
        widget=forms.TextInput(
            attrs={
                "class": "form-control",
                "minlength": "2",
                "maxlength": "30",
                "id": "first_name",
            }
        ),
    )

    last_name = forms.CharField(
        min_length=2,
        max_length=30,
        required=True,
        widget=forms.TextInput(
            attrs={
                "class": "form-control",
                "minlength": "2",
                "maxlength": "30",
                "id": "last_name",
            }
        ),
    )

    email = forms.EmailField(
        max_length=60,
        required=True,
        widget=forms.EmailInput(attrs={"class": "form-control", "id": "email"}),
    )

    bvn = forms.IntegerField(
        required=False,
        widget=forms.NumberInput(attrs={"class": "form-control", "id": "bvn"})    
    )

    password1 = forms.CharField(
        required=True,
        min_length=8,
        widget=forms.PasswordInput(
            attrs={"class": "form-control", "id": "floatingPassword1", "minlength": "8"}
        ),
    )

    password2 = forms.CharField(
        required=True,
        min_length=8,
        widget=forms.PasswordInput(
            attrs={"class": "form-control", "id": "floatingPassword2", "minlength": "8"}
        ),
    )

    class Meta:
        model = Account
        fields = (
            "first_name",
            "last_name",
            "email",
            "password1",
            "password2",
        )
    """
    def save(self, commit=True):
        user            = super(SignUpForm, self).save(commit=False) 
        user.first_name = self.cleaned_data['first_name']
        user.last_name  = self.cleaned_data['last_name']
        user.username   = self.cleaned_data['username']
        user.email      = self.cleaned_data['username']
        
        if commit:
            user.save()
        
        return user"""