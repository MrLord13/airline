from django.shortcuts import render, redirect
from django.contrib.auth import logout


# Create your views here.
def dashboard(request):
    data = {}

    return render(request, 'panel/dashboard.html', data)


def logout_view(request):
    logout(request)
    return redirect(to='home_page')
