from django import forms
from .models import Post, Comment


class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ('image', 'caption')
        widgets = {
            'caption': forms.Textarea(attrs={
                'placeholder': 'Write a caption...',
                'rows': 4,
                'class': 'form-input',
            }),
            'image': forms.FileInput(attrs={'class': 'hidden', 'id': 'post-image-input'}),
        }


class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ('text',)
        widgets = {
            'text': forms.TextInput(attrs={
                'placeholder': 'Add a comment...',
                'class': 'comment-input',
            })
        }