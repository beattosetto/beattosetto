from django import forms
from .models import Collection


class CreateCollectionForm(forms.ModelForm):
    """Form for creating the collection"""
    collection_list = forms.ImageField(required=True, label='Image')
    name = forms.CharField(required=True, label='Name')
    description = forms.CharField(required=True, widget=forms.Textarea, label='Description')

    class Meta:
        model = Collection
        fields = ['collection_list', 'name', 'description']