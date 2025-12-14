from django import forms
from .models import BBSPost, BBSComment


class BBSPostForm(forms.ModelForm):
    """掲示板投稿フォーム"""

    class Meta:
        model = BBSPost
        fields = ['title', 'content', 'report']
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'タイトルを入力してください',
                'maxlength': '200',
                'required': True
            }),
            'content': forms.Textarea(attrs={
                'class': 'form-control',
                'placeholder': '本文を入力してください',
                'rows': 5,
                'required': True
            }),
            'report': forms.Select(attrs={
                'class': 'form-control'
            }),
        }
        labels = {
            'title': 'タイトル',
            'content': '本文',
            'report': '日報（任意）',
        }
        help_texts = {
            'report': '関連する日報がある場合は選択してください',
        }

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        
        # reportフィールドを任意にする
        self.fields['report'].required = False

class BBSCommentForm(forms.ModelForm):
    """掲示板コメントフォーム"""

    class Meta:
        model = BBSComment
        fields = ['content']
        widgets = {
            'content': forms.Textarea(attrs={
                'class': 'form-control',
                'placeholder': 'コメントを入力してください',
                'rows': 3,
                'required': True
            }),
        }
        labels = {
            'content': '',
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['content'].required = True
