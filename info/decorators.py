from django.http import HttpResponse
from django.shortcuts import redirect


def unauthenticated_user(view_func):
    def wrapper_func(request, *args, kwargs):
        if request.user.is_authenticated:
            return redirect('home')
        else:
            return view_func(request, *args, kwargs)

    return wrapper_func


def allowed_users(allowed_roles=[]):
    def decorator(view_func):
        def wrapper_func(request):

            group = None
            if request.user.groups.exists():
                group = request.user.groups.all()[0].name

            if group in allowed_roles:
                return view_func(request)
            else:
                return HttpResponse('You are not authorized to view this page log in <a href=/login>here.</a>')
        return wrapper_func
    return decorator


def allowed_users1(allowed_roles=[]):
    def decorator(view_func):
        def wrapper_func(request, pk_test):

            group = None
            if request.user.groups.exists():
                group = request.user.groups.all()[0].name

            if group in allowed_roles:
                return view_func(request)
            else:
                return HttpResponse('You are not authorized to view this page log in <a href=/login>here.</a>')
        return wrapper_func
    return decorator


def admin_only(view_func):
    def wrapper_function(request, *args, kwargs):
        group = None
        if request.user.groups.exists():
            group = request.user.groups.all()[0].name

        if group == 'customer':
            return redirect('user-page')

        if group == 'admin':
            return view_func(request, *args, kwargs)

    return wrapper_function


def auth(request):
    if request.user.is_authenticated:
        return HttpResponse('You are not authorized to view this page log in <a href=/login>here.</a>')
    else:
        return redirect('/login')
