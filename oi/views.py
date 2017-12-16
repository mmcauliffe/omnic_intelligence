from django.shortcuts import render


# Create your views here.

def index(request):
    return render(request, 'oi/base.html', {'title': 'Omnic Intelligence'})
