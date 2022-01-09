from .models import Comment, FileUpload
from django import forms

class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ('content',)

class FileUploadForm(forms.ModelForm):
    class Meta:
        model = FileUpload
        fields = ['title', 'imgfile', 'content']