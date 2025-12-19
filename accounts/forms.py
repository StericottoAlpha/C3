from django import forms
from django.contrib.auth import authenticate,get_user_model

User = get_user_model()

class LoginForm(forms.Form):
    """Login form"""
    username = forms.CharField(
        label='User ID',
        max_length=150,
        widget=forms.TextInput(attrs={
            'class': 'form-input',
            'placeholder': 'sample',
        })
    )
    password = forms.CharField(
        label='Password',
        widget=forms.PasswordInput(attrs={
            'class': 'form-input',
            'placeholder': '********',
        })
    )

    def __init__(self, *args, **kwargs):
        self.user = None
        super().__init__(*args, **kwargs)

    def clean(self):
        cleaned_data = super().clean()
        username = cleaned_data.get('username')
        password = cleaned_data.get('password')

        if username and password:
            self.user = authenticate(username=username, password=password)
            if self.user is None:
                raise forms.ValidationError('ID or password is incorrect')
            if not self.user.is_active:
                raise forms.ValidationError('This account has been disabled')

        return cleaned_data

    def get_user(self):
        return self.user



class StaffEditForm(forms.ModelForm):
    class Meta:
        model = User
        # 編集できる項目：氏名、権限、所属店舗
        fields = ('last_name', 'first_name', 'user_type', 'store')
        labels = {
            'last_name': '姓',
            'first_name': '名',
            'user_type': '権限',
            'store': '所属店舗',
        }
        widgets = {
            'last_name': forms.TextInput(attrs={'class': 'border border-gray-300 rounded px-3 py-2 w-full'}),
            'first_name': forms.TextInput(attrs={'class': 'border border-gray-300 rounded px-3 py-2 w-full'}),
            'user_type': forms.Select(attrs={'class': 'border border-gray-300 rounded px-3 py-2 w-full'}),
            'store': forms.Select(attrs={'class': 'border border-gray-300 rounded px-3 py-2 w-full'}),
        }