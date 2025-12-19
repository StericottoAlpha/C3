from django import forms
from django.contrib.auth import authenticate, get_user_model

# ユーザーモデルを取得
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

#ユーザー登録用フォーム
class SignupForm(forms.ModelForm):
    password = forms.CharField(
        label='パスワード', 
        widget=forms.PasswordInput(attrs={'class': 'form-control'})
    )

    class Meta:
        model = User
        # 登録に必要なフィールドを定義
        fields = ['user_id', 'last_name', 'first_name', 'email', 'password', 'store', 'user_type']
        widgets = {
            'user_id': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'store': forms.Select(attrs={'class': 'form-select'}),
            'user_type': forms.Select(attrs={'class': 'form-select'}),
        }
        labels = {
            'store': '所属店舗',
            'user_type': '権限',
        }

    def save(self, commit=True):
        # パスワードをハッシュ化して保存する処理
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password"])
        if commit:
            user.save()
        return user


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
