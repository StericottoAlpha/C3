from django.shortcuts import render, redirect
from django.contrib.auth import login
from django.views.decorators.http import require_http_methods

from .forms import LoginForm
from django.contrib.auth.decorators import login_required

@login_required
def profile(request):
    return render(request, 'accounts/profile.html')



@require_http_methods(["GET", "POST"])
def login_view(request):
    """ログイン画面"""
    if request.user.is_authenticated:
        return redirect('common:index')

    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect('common:index')
    else:
        form = LoginForm()

    return render(request, 'accounts/login.html', {'form': form})
