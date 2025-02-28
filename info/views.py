import math
import json
from django.contrib.auth import get_user_model
from .decorators import allowed_users, allowed_users1, auth
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from users.forms import *
from .models import *
from django.http import HttpResponseRedirect, HttpResponse
from users.models import Profile
from django.contrib import messages
from django.core.paginator import Paginator
from .filters import ClientFilter, StaffFilter
from django.http import QueryDict


# redirects from index to the login page or landing page if authenticated.
@login_required
def index(request):
    if request.user.is_authenticated:
        return redirect('/land')
    else:
        return redirect('/login')


# This is the second part of the landing page auth flow where the workers group is verified.
@login_required
@allowed_users(allowed_roles=['Worker'])
def wok(request):
    auth(request)
    return render(request, "info/land_worker.html", {})

@login_required
@allowed_users(allowed_roles=['Coordinator'])
def cor(request):
    auth(request)
    return render(request, "info/land_coordinator.html", {})

@login_required
@allowed_users(allowed_roles=['Bookeeper'])
def bok(request):
    auth(request)
    return render(request, "info/land_bookeeper.html", {})


# This is the first part of the landing page auth flow where the workers group
# is retrived and redirected to the verify page.
@login_required
def land(request):
    auth(request)
    user_group = request.user.groups.values_list('name', flat=True)
    user_group = str(user_group[0])


    if user_group == 'Worker':
        return redirect('land/worker')

    if user_group == 'Supervisor':
        return redirect('land/supervisor')

    if user_group == 'Coordinator':
        return redirect('land/coordinator')

    if user_group == 'Bookeeper':
        return redirect('land/bookeeper')


# this redirects to the right help page, no type auth is used as if the page is leaked no actual data is compromised.

@login_required
def help1(request):

    user_group = request.user.groups.values_list('name', flat=True)
    user_group = str(user_group[0])


    if user_group == 'Worker':
        return render(request, "info/Staff/help/help_worker.html", {'usertype': user_group})

    if user_group == 'Coordinator':
        return render(request, "info/Staff/help/help_coordinator.html", {'usertype': user_group})

    if user_group == 'Bookeeper':
        return render(request, "info/Staff/help/help_bookeeper.html", {'usertype': user_group})


# redirects to the about page.
@login_required
def about(request):
    auth(request)
    return render(request, "info/about.html", {})


# view user entries in the database.
@login_required
@allowed_users(allowed_roles=['Coordinator', 'Bookeeper'])
def viewstaff(request):
    releng = (str(request))
    profile1 = Profile.objects.all()
    user_group = request.user.groups.values_list('name', flat=True)
    user_group = str(user_group[0])

    # sets up paging
    numb = profile1.count()
    numb = math.ceil(numb / 4)
    looper = list(range(1, numb + 1))
    p = Paginator(profile1.order_by('staff_fname'), 4)
    page = request.GET.get('page')
    deppage = p.get_page(page)
    directq = ''
    if "staff_id=" in releng:
        final = releng.split('+')
        final1 = final[0].replace("""<WSGIRequest: GET '/viewstaff?staff_id=ID%28""", '').replace("%29", '')
        query = {'staff_id': str(final1)}
        directq = QueryDict('', mutable=True)
        directq.update(query)
    myFilter = StaffFilter(directq, queryset=Profile.objects.all())
    if "staff_id=" in releng:
        deppage = myFilter.qs
    dropdown_varibles = Profile.objects.all().values_list('staff_id', 'staff_fname', 'staff_lname')
    dropdown = ['Error'] * len(dropdown_varibles)
    counter = 0
    for i in dropdown_varibles:
        dropdown[counter] = 'ID(' + str(i[0]) + ')' + ' ' + i[1] + ', ' + i[2]
        counter += 1
    dropdown = json.dumps(list(dropdown))
    return render(request, 'info/Staff/viewstaff.html', {'profile': profile1, 'usertype': user_group, 'pages': deppage, 'looper': looper, 'dropdown': dropdown, 'myFilter': myFilter})


# Adds a client into the system.
@login_required
@allowed_users(allowed_roles=['Coordinator', 'Bookeeper'])
def addclient(request):

    user_group = request.user.groups.values_list('name', flat=True)
    user_group = str(user_group[0])

    if request.method == "POST":
        form = ClientForm(request.POST)
        if form.is_valid():
            form.full_clean()
            client_fname = form.cleaned_data["client_fname"]
            client_lname = form.cleaned_data["client_lname"]
            client_phone = form.cleaned_data["client_phone"]
            client_address = form.cleaned_data["client_address"]
            client_city = form.cleaned_data["client_city"]
            client_max_hours = form.cleaned_data["client_max_hours"]
            client_km = form.cleaned_data["client_km"]
            client_notes = form.cleaned_data["client_notes"]
            t = Client(client_fname=client_fname, client_lname=client_lname, client_phone=client_phone,
                       client_address=client_address, client_city=client_city, client_max_hours=client_max_hours,
                       client_km=client_km, client_notes=client_notes, client_status='Active')
            t.save()
        if form.is_valid():
            messages.success(request, f'Added Client: {client_fname}, {client_lname} Sucsessfully')
            return HttpResponseRedirect('/addclient')
        else:
            form = ClientForm()
            return render(request, 'info/Client/addclient.html', {'form': form, 'usertype': user_group})

    else:
        form = ClientForm()
        return render(request, 'info/Client/addclient.html', {'form': form, 'usertype': user_group})


# Allows the viewing of clients in the database.
@login_required
@allowed_users(allowed_roles=['Coordinator', 'Bookeeper'])
def viewclient(request):
    releng = (str(request))
    client = Client.objects.all()
    user_group = request.user.groups.values_list('name', flat=True)
    user_group = str(user_group[0])
    numb = client.count()
    numb = math.ceil(numb / 4)
    looper = list(range(1, numb + 1))
    p = Paginator(client.order_by('client_fname'), 4)
    page = request.GET.get('page')
    deppage = p.get_page(page)
    directq = ''
    if "client_id=" in releng:
        final = releng.split('+')
        final1 = final[0].replace("""<WSGIRequest: GET '/viewclient?client_id=CID%28""", '').replace("%29", '')
        query = {'client_id': str(final1)}
        directq = QueryDict('', mutable=True)
        directq.update(query)
    myFilter = ClientFilter(directq, queryset=Client.objects.all())
    if "client_id=" in releng:
        deppage = myFilter.qs
    dropdown_varibles = Client.objects.all().values_list('client_id', 'client_fname', 'client_lname')
    dropdown = ['Error'] * len(dropdown_varibles)
    counter = 0
    for i in dropdown_varibles:
        dropdown[counter] = 'CID(' + str(i[0]) + ')' + ' ' + i[1] + ', ' + i[2]
        counter += 1
    dropdown = json.dumps(list(dropdown))
    return render(request, 'info/Client/viewclient.html', {'client': client, 'usertype': user_group, 'pages': deppage, 'looper': looper, "myFilter": myFilter, 'dropdown': dropdown})


# Allows the modification of clients already in the database.
@login_required
@allowed_users1(allowed_roles=['Coordinator', 'Bookeeper'])
def modclient(request):
    user_group = request.user.groups.values_list('name', flat=True)
    user_group = str(user_group[0])

    test = str(request)
    y = ''
    for x in test:
        if x.isnumeric():
            y = y + x

    clientinfo = Client.objects.filter(client_id=y)
    if request.method == "POST":
        form = ClientForm(request.POST)
        if form.is_valid():
            form.full_clean()
            client_fname = form.cleaned_data["client_fname"]
            client_status = form.cleaned_data["client_status"]
            client_lname = form.cleaned_data["client_lname"]
            client_phone = form.cleaned_data["client_phone"]
            client_address = form.cleaned_data["client_address"]
            client_city = form.cleaned_data["client_city"]
            client_max_hours = form.cleaned_data["client_max_hours"]
            client_km = form.cleaned_data["client_km"]
            client_notes = form.cleaned_data["client_notes"]

            Client.objects.filter(pk=y).update(client_fname=client_fname, client_lname=client_lname,
                                               client_phone=client_phone, client_address=client_address,
                                               client_city=client_city, client_max_hours=client_max_hours,
                                               client_km=client_km, client_notes=client_notes,
                                               client_status=client_status)
        if form.is_valid():
            messages.success(request, f'Modded Client {client_fname}, {client_lname} Sucsessfully')
            return HttpResponseRedirect('/viewclient')
        else:
            for i in clientinfo:
                form = ClientForm(
                    initial={'client_fname': i.client_fname, 'client_lname': i.client_lname,
                             'client_phone': i.client_phone,
                             'client_address': i.client_address, 'client_city': i.client_city,
                             'client_max_hours': i.client_max_hours,
                             'client_km': i.client_km, 'client_notes': i.client_notes, 'client_status': i.client_status,
                             'gh_id': i.client_fname})
                return render(request, 'info/Client/modclient.html',
                              {'getid': i.gh_id, 'clientinfo': clientinfo, 'usergroup': user_group,
                               'form': form, 'usertype': user_group})

    else:
        for i in clientinfo:
            phone = ''' type=text name=client_phone value=''' + i.client_phone + ''' class=form-control maxlength=13 pattern=[0-9]{3}-[0-9]{3}-[0-9]{4} required= id=id_client_phone'''
            form = ClientForm(
                initial={'client_fname': i.client_fname, 'client_lname': i.client_lname, 'client_phone': i.client_phone,
                         'client_address': i.client_address, 'client_city': i.client_city,
                         'client_max_hours': i.client_max_hours,
                         'client_km': i.client_km, 'client_notes': i.client_notes, 'client_status': i.client_status,
                         'gh_id': i.client_fname})
            return render(request, 'info/Client/modclient.html',
                          {'clientinfo': clientinfo, 'usergroup': user_group,
                           'form': form, 'phone': phone, 'usertype': user_group})


# Adds departments into the database.
@login_required
@allowed_users(allowed_roles=['Coordinator', 'Bookeeper'])
def adddep(request):
    user_group = request.user.groups.values_list('name', flat=True)
    user_group = (user_group[0])

    if request.method == "POST":
        form = Departmentform(request.POST)
        if form.is_valid():
            form.full_clean()
            dep_code = form.cleaned_data["dep_code"]
            dep_name = form.cleaned_data["dep_name"]
            dep_desc = form.cleaned_data["dep_desc"]
            ero = Department.objects.filter(dep_code=dep_code)
            if ero != 0:
                messages.success(request, 'Department code exists', extra_tags='error')
                form = Departmentform(
                    initial={'dep_name': dep_name, 'dep_desc': dep_desc})
                return render(request, 'info/Dep/adddep.html',
                              {'usergroup': user_group, 'form': form})
            t = Department(dep_code=dep_code, dep_status='Active', dep_name=dep_name, dep_desc=dep_desc)
            t.save()
        messages.success(request, f'Added Department: {dep_name} Sucsessfully', extra_tags='submit')
        return HttpResponseRedirect('/adddep')

    else:
        form = Departmentform()
        return render(request, 'info/Dep/adddep.html', {'form': form, 'usertype': user_group})

@login_required
@allowed_users(allowed_roles=['Coordinator', 'Bookeeper'])
def viewdep(request):
    user_group = request.user.groups.values_list('name', flat=True)
    user_group = str(user_group[0])
    department = Department.objects.all()
    numb = department.count()
    numb = math.ceil(numb / 5)
    looper = list(range(1, numb + 1))
    p = Paginator(Department.objects.all(), 5)
    page = request.GET.get('page')
    deppage = p.get_page(page)

    return render(request, 'info/Dep/viewdep.html', {'dep': department, 'usertype': user_group, 'pages': deppage, 'looper': looper})

@login_required
@allowed_users1(allowed_roles=['Coordinator', 'Bookeeper'])
def moddep(request):
    user_group = request.user.groups.values_list('name', flat=True)
    user_group = str(user_group[0])

    test = str(request)
    y = test.replace("<WSGIRequest: GET '/moddep/", "").replace("/'>", "")
    y = y.replace("<WSGIRequest: POST '/moddep/", "")

    departmentinfo = Department.objects.filter(dep_code=y)
    if request.method == "POST":
        form = Departmentform(request.POST)
        if form.is_valid():
            form.full_clean()
            dep_name = form.cleaned_data["dep_name"]
            dep_status = form.cleaned_data["dep_status"]
            dep_desc = form.cleaned_data["dep_desc"]

            Department.objects.filter(dep_code=y).update(dep_name=dep_name, dep_status=dep_status, dep_desc=dep_desc)
        messages.success(request, f'Modded Department {dep_name} Sucsessfully')
        return HttpResponseRedirect('/viewdep')

    else:
        for i in departmentinfo:
            form = Departmentform(
                initial={'dep_name': i.dep_name, 'dep_status': i.dep_status, 'dep_desc': i.dep_desc})
            return render(request, 'info/Dep/moddep.html',
                          {'depid': i.dep_code, 'depinfo': departmentinfo, 'usergroup': user_group, 'form': form, 'usertype': user_group})

@login_required
@allowed_users1(allowed_roles=['Coordinator', 'Bookeeper'])
def changeuserpass(request):
    user_group = request.user.groups.values_list('name', flat=True)
    user_group = str(user_group[0])

    test = str(request)
    y = test.replace("<WSGIRequest: GET '/passuser/", "").replace("/'>", "")
    y = y.replace("<WSGIRequest: POST '/passuser/", "")

    if request.method == "POST":
        form = AdminPassChange(request.POST)
        if form.is_valid():
            form.full_clean()
            stid = Profile.objects.filter(staff_id=y).values_list('user_id', flat=True)
            User = get_user_model()
            useride = get_object_or_404(User, id=stid[0])
            password1 = form.cleaned_data["password1"]
            password2 = form.cleaned_data["password2"]
            if password1 == password2:
                useride.set_password(password1)
                useride.save()
        messages.success(request, f'Updated User Password Sucsessfully')
        return HttpResponseRedirect('/viewstaff')

    else:

        form = AdminPassChange()
        return render(request, 'info/Staff/cahngestaffpass.html', {'usergroup': user_group, 'form': form, 'usertype': user_group})

