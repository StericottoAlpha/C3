from django.shortcuts import render
from django.contrib.auth.decorators import login_required

@login_required
def index(request):
    """
    ホーム画面を表示する
    """
    return render(request, 'common/index.html')