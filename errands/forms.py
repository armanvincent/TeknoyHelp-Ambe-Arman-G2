from django import forms
from django.utils import timezone

from accounts.forms import BootstrapFormMixin
from .models import Category, ErrandRequest


class ErrandForm(BootstrapFormMixin, forms.ModelForm):
    deadline = forms.DateTimeField(
        widget=forms.DateTimeInput(attrs={'type': 'datetime-local'}, format='%Y-%m-%dT%H:%M'),
        input_formats=['%Y-%m-%dT%H:%M'],
        help_text='The date and time the errand must be done.',
    )

    class Meta:
        model = ErrandRequest
        fields = ('category', 'title', 'description', 'location', 'deadline', 'reward')
        widgets = {'description': forms.Textarea(attrs={'rows': 4})}
        labels = {'reward': 'Reward (PHP)'}

    def clean_title(self):
        title = self.cleaned_data['title'].strip()
        if len(title) < 5:
            raise forms.ValidationError('Title must be at least 5 characters.')
        return title

    def clean_description(self):
        description = self.cleaned_data['description'].strip()
        if len(description) < 10:
            raise forms.ValidationError('Please describe the errand in at least 10 characters.')
        return description

    def clean_deadline(self):
        deadline = self.cleaned_data['deadline']
        if deadline <= timezone.now():
            raise forms.ValidationError('The deadline must be in the future.')
        return deadline


class ErrandFilterForm(BootstrapFormMixin, forms.Form):
    SORT_CHOICES = [
        ('newest', 'Newest first'),
        ('reward_high', 'Highest reward'),
        ('reward_low', 'Lowest reward'),
        ('deadline', 'Earliest deadline'),
    ]

    q = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={'placeholder': 'Search title, details or location'}),
    )
    category = forms.ModelChoiceField(
        queryset=Category.objects.all(), required=False, empty_label='All categories'
    )
    min_reward = forms.DecimalField(
        required=False, min_value=0, max_digits=8, decimal_places=2,
        widget=forms.NumberInput(attrs={'placeholder': 'Min reward'}),
    )
    max_reward = forms.DecimalField(
        required=False, min_value=0, max_digits=8, decimal_places=2,
        widget=forms.NumberInput(attrs={'placeholder': 'Max reward'}),
    )
    sort = forms.ChoiceField(choices=SORT_CHOICES, required=False)

    def clean(self):
        cleaned = super().clean()
        minimum = cleaned.get('min_reward')
        maximum = cleaned.get('max_reward')
        if minimum is not None and maximum is not None and minimum > maximum:
            raise forms.ValidationError('Minimum reward cannot be higher than maximum reward.')
        return cleaned