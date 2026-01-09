from django import forms
from .models import DailyReport, ReportImage


class DailyReportForm(forms.ModelForm):
    """Daily Report Registration Form"""

    # Single image upload field
    image = forms.ImageField(
        required=False,
        label='写真',
        widget=forms.FileInput(attrs={
            'class': 'form-control',
            'accept': 'image/*'
        })
    )

    class Meta:
        model = DailyReport
        fields = ['genre', 'location', 'title', 'content', 'post_to_bbs']
        widgets = {
            'genre': forms.Select(attrs={
                'class': 'form-select',
                'required': True
            }),
            'location': forms.Select(attrs={
                'class': 'form-select',
                'required': True
            }),
            'title': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': '例：レジで釣銭ミスが発生',
                'required': True,
                'maxlength': 200
            }),
            'content': forms.Textarea(attrs={
                'class': 'form-control',
                'placeholder': '例：状況／原因／対応／再発防止を簡潔に',
                'rows': 5,
                'required': True
            }),
            'post_to_bbs': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
        }
        labels = {
            'genre': 'ジャンル',
            'location': '発生場所',
            'title': '件名',
            'content': '内容',
            'post_to_bbs': '掲示板に投稿',
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # 「---------」を日本語に
        if 'genre' in self.fields:
            self.fields['genre'].empty_label = '選択してください'
        if 'location' in self.fields:
            self.fields['location'].empty_label = '選択してください'

    def clean_title(self):
        """Validate title"""
        title = self.cleaned_data.get('title')
        if not title or len(title.strip()) == 0:
            raise forms.ValidationError('件名を入力してください。')
        if len(title) > 200:
            raise forms.ValidationError('件名は200文字以内で入力してください。')
        return title.strip()

    def clean_content(self):
        """Validate content"""
        content = self.cleaned_data.get('content')
        if not content or len(content.strip()) == 0:
            raise forms.ValidationError('内容を入力してください。')
        return content.strip()
