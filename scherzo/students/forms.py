from django import forms
from tracks.models import Track


class CourseEnrollForm(forms.Form):
	course = forms.ModelChoiceField(queryset=Track.objects.all(), widget=forms.HiddenInput)