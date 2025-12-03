from django.shortcuts import render

from .models import PageVisit


def index(request):
    # データベースに新しいレコードを追加
    PageVisit.objects.create(message='ページが訪問されました')

    # 全てのレコードを取得
    visits = PageVisit.objects.all()

    return render(request, 'common/index.html', {'visits': visits})
