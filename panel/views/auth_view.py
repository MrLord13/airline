from django.contrib.auth import login
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse

from appuser.models import MyUser


def login_view(request):
    data = dict()
    if request.method == 'POST':
        if 'username' in request.POST and 'password' in request.POST:
            username = request.POST['username']
            password = request.POST['password']
            try:
                user = MyUser.objects.get(username=username)
                if user.check_password(password):
                    if user.is_active:
                        login(request, user)
                        return HttpResponseRedirect(reverse('dashboard'))
                    else:
                        data['message'] = 'Your account is deactivated'
                else:
                    data['message'] = 'username or password is incorrect'
            except:
                data['message'] = 'username or password is incorrect'
        else:
            data['message'] = 'username or password is incorrect'

    return render(request, 'panel/login.html', data)
