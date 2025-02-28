# views.py
from django.http import HttpResponseRedirect
from django.shortcuts import render, redirect
from .forms import RegisterForm, ProfileForm
from info.decorators import allowed_users, allowed_users1
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth.views import PasswordChangeView
from django.contrib.auth.models import Group, User
from users.models import Profile
from django.contrib.auth import get_user_model
from django.contrib import messages
from .forms import UserEdit
import json


# Create your views here.
@login_required
@allowed_users(allowed_roles=['Coordinator', 'Bookeeper'])
def register(request):
    user_group = request.user.groups.values_list('name', flat=True)
    user_group = str(user_group[0])

    if request.method == "POST":
        form = RegisterForm(request.POST)
        form1 = ProfileForm(request.POST)
        staff_fname = 'error'
        staff_lname = 'error'
        sunf = ''
        monf = ''
        tuef = ''
        wedf = ''
        thuf = ''
        frif = ''
        satf = ''
        sunst = ''
        sunend = ''
        monst = ''
        monend = ''
        tuest = ''
        tueend = ''
        wedst = ''
        wedend = ''
        thust = ''
        thuend = ''
        frist = ''
        friend = ''
        satst = ''
        satend = ''
        sunf = sunst + " - " + sunend
        monf = monst + " - " + monend
        tuef = tuest + " - " + tueend
        wedf = wedst + " - " + wedend
        thuf = thust + " - " + thuend
        frif = frist + " - " + friend
        satf = satst + " - " + satend
        print(request.POST)
        if form1.is_valid():
            neec = str(request.POST['username'])
            form1.full_clean()
            type_code = request.POST.get('type')
            if type_code == 'Worker':
                sunst = request.POST.get('sunSt')
                sunend = request.POST.get('sunEnd')
                monst = request.POST.get('monSt')
                monend = request.POST.get('monEnd')
                tuest = request.POST.get('tueSt')
                tueend = request.POST.get('tueEnd')
                wedst = request.POST.get('wedSt')
                wedend = request.POST.get('wedEnd')
                thust = request.POST.get('thuSt')
                thuend = request.POST.get('thuEnd')
                frist = request.POST.get('friSt')
                friend = request.POST.get('friEnd')
                satst = request.POST.get('satSt')
                satend = request.POST.get('satEnd')
                sunf = sunst + " - " + sunend
                monf = monst + " - " + monend
                tuef = tuest + " - " + tueend
                wedf = wedst + " - " + wedend
                thuf = thust + " - " + thuend
                frif = frist + " - " + friend
                satf = satst + " - " + satend
            staff_fname = form1.cleaned_data["Firstname"]
            staff_lname = form1.cleaned_data["Lastname"]
            staff_phone = form1.cleaned_data["Phone"]
            staff_address = form1.cleaned_data["Fulladdress"]
            staff_city = form1.cleaned_data["City"]
            sun_avail = sunf
            mon_avail = monf
            tue_avail = tuef
            wed_avail = wedf
            thu_avail = thuf
            fri_avail = frif
            sat_avail = satf
            staff_notes = form1.cleaned_data["Notes"]
            User = get_user_model()
            ero = User.objects.filter(username=neec)
            if len(ero) == 0:
                t = 1
            else:
                graph = 0
                if type_code == 'Worker':
                    try:
                        sunf = sun_avail.split(" - ")
                        monf = mon_avail.split(" - ")
                        tuef = tue_avail.split(" - ")
                        wedf = wed_avail.split(" - ")
                        thuf = thu_avail.split(" - ")
                        frif = fri_avail.split(" - ")
                        satf = sat_avail.split(" - ")
                        sunst = sunf[0]
                        sunend = sunf[1]
                        monst = monf[0]
                        monend = monf[1]
                        tuest = tuef[0]
                        tueend = tuef[1]
                        wedst = wedf[0]
                        wedend = wedf[1]
                        thust = thuf[0]
                        thuend = thuf[1]
                        frist = frif[0]
                        friend = frif[1]
                        satst = satf[0]
                        satend = satf[1]
                        graph = 1
                    except:
                        w = "a"
                graph = json.dumps(graph)
                phone = '''<input type="tel" name="Phone" class="form-control" pattern="[0-9]{3}-[0-9]{3}-[0-9]{4}" required="" id="id_Phone"  value="''' + staff_phone + '''">'''
                print(phone)
                messages.success(request, 'Username Taken', extra_tags='error')
                return render(request, 'register/register.html',
                              {'graph': graph, 'form1': form1,
                               'tyype': type_code, 'sunSt': sunst, 'sunEnd': sunend, 'monSt': monst,
                               'monEnd': monend,
                               'tueSt': tuest, 'tueEnd': tueend, 'wedSt': wedst, 'wedEnd': wedend, 'thuSt': thust,
                               'thuEnd': thuend, 'friSt': frist, 'phone': phone, 'friEnd': friend,
                               'satSt': satst,
                               'satEnd': satend, 'usertype': user_group})
            form.save()
            User = get_user_model()
            nameg = User.objects.filter(username=neec).values_list('id', flat=True)
            nameg = str(nameg[0])
            Profile.objects.filter(user_id=nameg).update(staff_fname=staff_fname, staff_lname=staff_lname,
                                                         type_code=type_code,
                                                         staff_phone=staff_phone,
                                                         staff_address=staff_address, staff_city=staff_city,
                                                        sun_avail=sun_avail, mon_avail=mon_avail,
                                                         tue_avail=tue_avail,
                                                         wed_avail=wed_avail, thu_avail=thu_avail, fri_avail=fri_avail,
                                                         sat_avail=sat_avail,
                                                         staff_notes=staff_notes, staff_status='Active', staff_id=nameg)
            user_set = User.objects.get(username=neec)
            ge_group = Group.objects.get(name=type_code)
            ge_group.user_set.add(user_set)
        messages.success(request, f'Added Staff Member {staff_fname}, {staff_lname} Sucsessfully', extra_tags='submit')
        return redirect("/addstaff")
    else:
        form = RegisterForm()
        form1 = ProfileForm()
    phone = '<input type="tel" name="Phone" value="" class="form-control" pattern="[0-9]{3}-[0-9]{3}-[0-9]{4}" required="" id="id_Phone">'
    return render(request, "register/register.html", {"form": form, 'form1': form1, 'phone': phone, 'usertype': user_group})


class Passwordviewss(PasswordChangeView):
    form_class = PasswordChangeForm
    success_url = '/land'

@login_required
@allowed_users1(allowed_roles=['Coordinator', 'Bookeeper'])
def modstaff(request):
    print(request.POST)
    print('test')
    user_group = request.user.groups.values_list('name', flat=True)
    user_group = str(user_group[0])

    test = str(request)
    y = test.replace("<WSGIRequest: GET '/modstaff/", "").replace("/'>", "")
    y = y.replace("<WSGIRequest: POST '/modstaff/", "")

    profileinfo = Profile.objects.filter(staff_id=y)
    if request.method == "POST":
        form = UserEdit(request.POST)
        form1 = ProfileForm(request.POST)
        sunf = ''
        monf = ''
        tuef = ''
        wedf = ''
        thuf = ''
        frif = ''
        satf = ''
        staff_fname = 'error'
        staff_lname = 'error'
        if form1.is_valid():
            form1.full_clean()
            type_code = request.POST.get('type')
            if type_code == 'Worker':
                sunst = request.POST.get('sunSt')
                sunend = request.POST.get('sunEnd')
                monst = request.POST.get('monSt')
                monend = request.POST.get('monEnd')
                tuest = request.POST.get('tueSt')
                tueend = request.POST.get('tueEnd')
                wedst = request.POST.get('wedSt')
                wedend = request.POST.get('wedEnd')
                thust = request.POST.get('thuSt')
                thuend = request.POST.get('thuEnd')
                frist = request.POST.get('friSt')
                friend = request.POST.get('friEnd')
                satst = request.POST.get('satSt')
                satend = request.POST.get('satEnd')
                sunf = sunst + " - " + sunend
                monf = monst + " - " + monend
                tuef = tuest + " - " + tueend
                wedf = wedst + " - " + wedend
                thuf = thust + " - " + thuend
                frif = frist + " - " + friend
                satf = satst + " - " + satend
            staff_fname = form1.cleaned_data["Firstname"]
            staff_lname = form1.cleaned_data["Lastname"]
            staff_phone = form1.cleaned_data["Phone"]
            staff_address = form1.cleaned_data["Fulladdress"]
            staff_city = form1.cleaned_data["City"]
            sun_avail = sunf
            mon_avail = monf
            tue_avail = tuef
            wed_avail = wedf
            thu_avail = thuf
            fri_avail = frif
            sat_avail = satf
            username1 = str(request.POST.get('uname'))
            staff_status = request.POST.get('status')
            staff_notes = form1.cleaned_data["Notes"]

            typee = Profile.objects.filter(staff_id=y).values_list('type_code', flat=True)
            if str(typee[0]) != type_code:
                if str(type_code) == 'Bookeeper':
                    group = Group.objects.get(id=2)
                if str(type_code) == 'Coordinator':
                    group = Group.objects.get(id=3)
                if str(type_code) == 'Worker':
                    group = Group.objects.get(id=5)
                user = User.objects.get(pk=y)
                user.groups.clear()
                group.user_set.add(user)

            Profile.objects.filter(pk=y).update(staff_fname=staff_fname, staff_lname=staff_lname,
                                                type_code=type_code,
                                                staff_phone=staff_phone,
                                                staff_address=staff_address, staff_city=staff_city,
                                                sun_avail=sun_avail, mon_avail=mon_avail,
                                                tue_avail=tue_avail,
                                                wed_avail=wed_avail, thu_avail=thu_avail, fri_avail=fri_avail,
                                                sat_avail=sat_avail,
                                                staff_notes=staff_notes, staff_status=staff_status)
            nameg = Profile.objects.filter(staff_id=y).values_list('user_id', flat=True)
            thatg = User.objects.filter(id=nameg[0]).values_list('username', flat=True)
            ero = User.objects.filter(username=username1)
            if username1 != thatg[0]:
                if len(ero) == 0:
                    user = User.objects.get(username=thatg[0])
                    user.username = username1
                    user.save()
                else:
                    graph = 0
                    if type_code == 'Worker':
                        try:
                            sunf = sun_avail.split(" - ")
                            monf = mon_avail.split(" - ")
                            tuef = tue_avail.split(" - ")
                            wedf = wed_avail.split(" - ")
                            thuf = thu_avail.split(" - ")
                            frif = fri_avail.split(" - ")
                            satf = sat_avail.split(" - ")
                            sunst = sunf[0]
                            sunend = sunf[1]
                            monst = monf[0]
                            monend = monf[1]
                            tuest = tuef[0]
                            tueend = tuef[1]
                            wedst = wedf[0]
                            wedend = wedf[1]
                            thust = thuf[0]
                            thuend = thuf[1]
                            frist = frif[0]
                            friend = frif[1]
                            satst = satf[0]
                            satend = satf[1]
                            graph = 1
                        except:
                            w = "a"
                    graph = json.dumps(graph)
                    phone = '''type=text name=Phone class=form-control id=id_Phone pattern=[0-9]{3}-[0-9]{3}-[0-9]{4} value=''' + staff_phone
                    messages.success(request, 'Username Taken', extra_tags='error')
                    return render(request, 'info/Staff/modstaff.html',
                                  {'graph': graph, 'proinfo': profileinfo, 'usergroup': user_group, 'form1': form1,
                                   'stat': staff_status,
                                   'tyype': type_code, 'sunSt': sunst, 'sunEnd': sunend, 'monSt': monst,
                                   'monEnd': monend,
                                   'tueSt': tuest, 'tueEnd': tueend, 'wedSt': wedst, 'wedEnd': wedend, 'thuSt': thust,
                                   'thuEnd': thuend, 'friSt': frist, 'phone': phone, 'friEnd': friend,
                                   'satSt': satst,
                                   'satEnd': satend, 'idf': y, 'unamev': thatg[0], 'usertype': user_group})
            if staff_status == 'Active':
                user = User.objects.get(username=thatg[0])
                user.is_active = True
                user.save()
            if staff_status == 'On Hold':
                user = User.objects.get(username=thatg[0])
                user.is_active = True
                user.save()
            if staff_status == 'Inactive':
                user = User.objects.get(username=thatg[0])
                user.is_active = False
                user.save()

        messages.success(request, f'Modded Staff Member {staff_fname}, {staff_lname} Sucsessfully', extra_tags='submit')
        return HttpResponseRedirect('/viewstaff')

    else:
        sunst = ""
        sunend = ""
        monst = ""
        monend = ""
        tuest = ""
        tueend = ""
        wedst = ""
        wedend = ""
        thust = ""
        thuend = ""
        frist = ""
        friend = ""
        satst = ""
        satend = ""
        nameg = Profile.objects.filter(staff_id=y).values_list('user_id', flat=True)
        thatg = User.objects.filter(id=nameg[0]).values_list('username', flat=True)
        for i in profileinfo:
            form1 = ProfileForm(
                initial={'Firstname': i.staff_fname, 'Lastname': i.staff_lname, 'Fulladdress': i.staff_address,
                         'City': i.staff_city, 'Phone': i.staff_phone, 'Notes': i.staff_notes})
            graph = 0
            if i.type_code == 'Worker':
                try:
                    sunf = i.sun_avail.split(" - ")
                    monf = i.mon_avail.split(" - ")
                    tuef = i.tue_avail.split(" - ")
                    wedf = i.wed_avail.split(" - ")
                    thuf = i.thu_avail.split(" - ")
                    frif = i.fri_avail.split(" - ")
                    satf = i.sat_avail.split(" - ")
                    sunst = sunf[0]
                    sunend = sunf[1]
                    monst = monf[0]
                    monend = monf[1]
                    tuest = tuef[0]
                    tueend = tuef[1]
                    wedst = wedf[0]
                    wedend = wedf[1]
                    thust = thuf[0]
                    thuend = thuf[1]
                    frist = frif[0]
                    friend = frif[1]
                    satst = satf[0]
                    satend = satf[1]
                    graph = 1
                except:
                    w = "a"
            graph = json.dumps(graph)
            phone = '''type=text name=Phone class=form-control id=id_Phone pattern=[0-9]{3}-[0-9]{3}-[0-9]{4} value=''' + i.staff_phone
            return render(request, 'info/Staff/modstaff.html',
                          {'graph': graph, 'proinfo': profileinfo, 'usergroup': user_group, 'form1': form1,
                           'stat': i.staff_status,
                           'tyype': i.type_code, 'sunSt': sunst, 'sunEnd': sunend, 'monSt': monst, 'monEnd': monend,
                           'tueSt': tuest, 'tueEnd': tueend, 'wedSt': wedst, 'wedEnd': wedend, 'thuSt': thust,
                           'thuEnd': thuend, 'friSt': frist, 'phone': phone, 'friEnd': friend, 'satSt': satst,
                           'satEnd': satend, 'idf': i.staff_id, 'unamev': thatg[0], 'usertype': user_group})
