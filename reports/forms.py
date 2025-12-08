from django import forms
from .models import DailyReport, ReportImage


class DailyReportForm(forms.ModelForm):
    """Daily Report Registration Form"""

    # Single image upload field
    image = forms.ImageField(
        required=False,
        label='Photo',
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
                'placeholder': 'Enter subject',
                'required': True,
                'maxlength': 200
            }),
            'content': forms.Textarea(attrs={
                'class': 'form-control',
                'placeholder': 'Enter comment',
                'rows': 5,
                'required': True
            }),
            'post_to_bbs': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
        }
        labels = {
            'genre': 'Genre',
            'location': 'Location',
            'title': 'Subject',
            'content': 'Comment',
            'post_to_bbs': 'Post to BBS',
        }

    def clean_title(self):
        """Validate title"""
        title = self.cleaned_data.get('title')
        if not title or len(title.strip()) == 0:
            raise forms.ValidationError('Please enter a subject.')
        if len(title) > 200:
            raise forms.ValidationError('Subject must be 200 characters or less.')
        return title.strip()

    def clean_content(self):
        """Validate content"""
        content = self.cleaned_data.get('content')
        if not content or len(content.strip()) == 0:
            raise forms.ValidationError('Please enter a comment.')
        return content.strip()
