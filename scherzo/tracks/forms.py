from django import forms
from django.forms.models import inlineformset_factory
from .models import Track, Module


ModuleFormSet = inlineformset_factory(Track, Module, 
	fields=['title', 'description'], extra=2, can_delete=True)