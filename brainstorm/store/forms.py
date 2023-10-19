# forms.py
from django.core.validators import MinValueValidator, MaxValueValidator
from django import forms
from .models import Review

class ReviewForm(forms.ModelForm):
    class Meta:
        model = Review
        fields = ['rating', 'comment']

rating = forms.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)]
    )