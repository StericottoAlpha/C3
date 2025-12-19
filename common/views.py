from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse

@login_required
def index(request):
    """
    ホーム画面を表示する
    """
    return render(request, 'common/index.html')

def health(request):
    """
    health end point
    """

    return HttpResponse(status=200)