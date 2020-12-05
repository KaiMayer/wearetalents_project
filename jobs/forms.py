from django import forms
from .models import JobPost


class SearchForm(forms.Form):
    query = forms.CharField()

