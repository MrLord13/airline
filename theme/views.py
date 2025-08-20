from django.shortcuts import render


def home(request):
    data = {}
    return render(request, 'index.html', data)


def blogs(request):
    data = {}

    return render(request, 'blogs.html', data)


def blog(request, pid):
    data = {}

    return render(request, 'blog.html', data)


def about(request):
    data = {}

    return render(request, 'aboutUs.html', data)


def contact(request):
    data = {}

    return render(request, 'contactUs.html', data)
