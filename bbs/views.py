from django.shortcuts import render
from django.contrib.auth.decorators import login_required

@login_required
def post_list(request):
    return render(request, 'bbs/list.html')
