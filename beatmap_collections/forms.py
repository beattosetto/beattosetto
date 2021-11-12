"""
This file contain form class that get the Collection and Beatmap from template to views.
"""
from django import forms
from .models import Collection, BACKGROUND_ALIGNMENT_CHOICES


class CreateCollectionForm(forms.ModelForm):
    """Form for creating the collection"""
    collection_list = forms.ImageField(required=False, label='Image')
    name = forms.CharField(required=True, label='Name', max_length=50)
    description = forms.CharField(required=True, widget=forms.Textarea, label='Description', max_length=500)
    allow_comment = forms.BooleanField(required=False, label='Allow Comments', widget=forms.CheckboxInput(attrs={'class': "form-check-input"}))
    background_align = forms.ChoiceField(label="", choices=BACKGROUND_ALIGNMENT_CHOICES, required=False, widget=forms.Select(attrs={'class': "form-select form-select-sm"}))

    class Meta:
        """Create field that contain collection list, name , description and tags."""
        model = Collection
        fields = ['collection_list', 'name', 'description', 'tags', 'allow_comment', 'background_align']


class AddBeatmapForm(forms.Form):
    """Form for adding beatmap using beatmap ID to the collection"""
    beatmap_id = forms.IntegerField(required=True, label='Beatmap ID')
    comment = forms.CharField(required=True, label='Comment', max_length=500)

    class Meta:
        """Create field that contain beatmap id & comment."""
        fields = ['beatmap', 'comment']


class AddCommentForm(forms.Form):
    """Form for adding comment to the collection"""
    comment = forms.CharField(required=True, label='Comment', max_length=500)

    class Meta:
        """Create field that contain comment."""
        fields = ['comment']
