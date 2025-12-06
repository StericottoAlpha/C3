from django.shortcuts import render
from django.contrib.auth.decorators import login_required

from .models import PageVisit


@login_required(login_url='/accounts/login/')
def index(request):
    # データベースに新しいレコードを追加
    PageVisit.objects.create(message='ページが訪問されました')

    # 全てのレコードを取得
    visits = PageVisit.objects.all()

    return render(request, 'common/index.html', {'visits': visits})
