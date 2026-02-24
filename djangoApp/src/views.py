from django.shortcuts import render

def home(request):
    return render(request, 'home.html')


def buyer(request):
    return render(request,'buyer.html')

def login(request):
    return render(request,'login.html')
