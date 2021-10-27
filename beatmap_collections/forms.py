from django import forms
from .models import Collection, BeatmapEntry


class CreateCollectionForm(forms.ModelForm):
    """Form for creating the collection"""
    collection_list = forms.ImageField(required=False, label='Image')
    name = forms.CharField(required=True, label='Name')
    description = forms.CharField(required=True, widget=forms.Textarea, label='Description')

    class Meta:
        model = Collection
        fields = ['collection_list', 'name', 'description']


class AddBeatmapForm(forms.Form):
    """Form for adding beatmap using beatmap ID to the collection"""
    beatmap_id = forms.IntegerField(required=True, label='Beatmap ID')
    comment = forms.CharField(required=True, label='Comment')

    class Meta:
        fields = ['beatmap', 'comment']