from django import forms
from .models import BBSPost, BBSComment

class BBSPostForm(forms.ModelForm):
    """掲示板投稿フォーム"""

    class Meta:
        model = BBSPost

        fields = ['title', 'genre', 'content', 'report']
        
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'form-control w-full',
                'placeholder': 'タイトルを入力してください',
                'maxlength': '200',
                'required': True
            }),

            'genre': forms.Select(attrs={
                'class': 'form-control w-full', # 他のフィールドに合わせて form-control を設定
            }),
            'content': forms.Textarea(attrs={
                'class': 'form-control w-full',
                'placeholder': '本文を入力してください',
                'rows': 5,
                'required': True
            }),
            'report': forms.Select(attrs={
                'class': 'form-control w-full'
            }),
        }
        labels = {
            'title': 'タイトル',
            'genre': 'ジャンル', # 3. ラベルを追加
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
        
        # モデルで default='report' 等を設定していない場合、
        # ここで空の選択肢を表示させない設定なども可能です
        # self.fields['genre'].empty_label = None 


# BBSCommentForm は変更なし
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