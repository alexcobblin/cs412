from django import forms
from .models import Post, Profile


class CreatePostForm(forms.ModelForm):
    '''A form to add a Post to the database.'''

    class Meta:
        '''Associate this form with the Post model; select fields to add.'''
        model = Post
        fields = ['caption']


class UpdateProfileForm(forms.ModelForm):
    '''A form to update a Profile in the database.'''

    class Meta:
        '''Associate this form with the Profile model; select fields to update.'''
        model = Profile
        fields = ['display_name', 'bio_text', 'profile_image_url']


class UpdatePostForm(forms.ModelForm):
    '''A form to update a Post in the database.'''

    class Meta:
        '''Associate this form with the Post model; select fields to update.'''
        model = Post
        fields = ['caption']