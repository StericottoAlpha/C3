from django.shortcuts import render
from django.contrib.auth.decorators import login_required

@login_required
def ai_dashboard(request):
    return render(request, 'ai_features/dashboard.html')

# Create your views here.
