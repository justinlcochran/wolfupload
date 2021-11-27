from django.forms import ModelForm
from django import forms
from django.db import models
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import Player, Role


class RoleForm(ModelForm):
	class Meta:
		model = Role
		fields = ['title', 'score', 'description', 'alignment', 'type']


class PlayerForm(ModelForm):

	name = forms.CharField(
		max_length=255,
		widget=forms.TextInput(attrs={'autofocus': True})
	)

	class Meta:
		model = Player
		fields = ['name']


class CreateUserForm(UserCreationForm):
	class Meta:
		model = User
		fields = ['username', 'email', 'password1', 'password2']
