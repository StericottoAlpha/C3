from django import forms
from .models import BBSPost


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
