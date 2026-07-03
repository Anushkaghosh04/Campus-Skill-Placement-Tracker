from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm

from .models import Profile, Skill, Resume, TARGET_ROLE_CHOICES


class RegisterForm(UserCreationForm):
    email = forms.EmailField(required=True)
    name = forms.CharField(max_length=150, required=True, label="Full Name")

    class Meta:
        model = User
        fields = ['username', 'name', 'email', 'password1', 'password2']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            field.widget.attrs.update({'class': 'form-control'})

    def save(self, commit=True):
        user = super().save(commit=commit)
        return user


class ProfileForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ['name', 'email', 'branch', 'semester', 'cgpa', 'projects_count',
                  'target_role', 'profile_photo']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'branch': forms.Select(attrs={'class': 'form-select'}),
            'semester': forms.NumberInput(attrs={'class': 'form-control', 'min': 1, 'max': 8}),
            'cgpa': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'min': 0, 'max': 10}),
            'projects_count': forms.NumberInput(attrs={'class': 'form-control', 'min': 0}),
            'target_role': forms.Select(attrs={'class': 'form-select'}),
            'profile_photo': forms.ClearableFileInput(attrs={'class': 'form-control'}),
        }


class SkillForm(forms.ModelForm):
    class Meta:
        model = Skill
        fields = ['name', 'category', 'proficiency']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. Python, React, MySQL'}),
            'category': forms.Select(attrs={'class': 'form-select'}),
            'proficiency': forms.Select(attrs={'class': 'form-select'}),
        }


class ResumeUploadForm(forms.ModelForm):
    class Meta:
        model = Resume
        fields = ['file']
        widgets = {
            'file': forms.ClearableFileInput(attrs={'class': 'form-control', 'accept': '.pdf'}),
        }

    def clean_file(self):
        file = self.cleaned_data.get('file')
        if file and not file.name.lower().endswith('.pdf'):
            raise forms.ValidationError("Only PDF files are supported.")
        return file


class TargetRoleForm(forms.Form):
    target_role = forms.ChoiceField(
        choices=TARGET_ROLE_CHOICES,
        widget=forms.Select(attrs={'class': 'form-select'}),
        label="Select Target Role"
    )


class StyledAuthenticationForm(AuthenticationForm):
    """Django's AuthenticationForm with Bootstrap classes applied."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['username'].widget.attrs.update({'class': 'form-control', 'autofocus': True})
        self.fields['password'].widget.attrs.update({'class': 'form-control'})
