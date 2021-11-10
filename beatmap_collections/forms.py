from django import forms
from taggit.managers import TaggableManager
from .models import Collection


class CreateCollectionForm(forms.ModelForm):
    """Form for creating the collection"""
    collection_list = forms.ImageField(required=False, label='Image')
    name = forms.CharField(required=True, label='Name', max_length=50)
    description = forms.CharField(required=True, widget=forms.Textarea, label='Description', max_length=500)

    class Meta:
        model = Collection
        fields = ['collection_list', 'name', 'description', 'tags']


class AddBeatmapForm(forms.Form):
    """Form for adding beatmap using beatmap ID to the collection"""
    beatmap_id = forms.IntegerField(required=True, label='Beatmap ID')
    comment = forms.CharField(required=True, label='Comment', max_length=500)

    class Meta:
        fields = ['beatmap', 'comment']


class AddCommentForm(forms.Form):
    """Form for adding comment to the collection"""
    comment = forms.CharField(required=True, label='Comment', max_length=500)

    class Meta:
        fields = ['comment']
