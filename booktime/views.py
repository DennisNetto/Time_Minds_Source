import datetime
from django.contrib.auth.decorators import login_required
from info.decorators import allowed_users, allowed_users1
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from .function_roll import *
from calendar import monthrange

# Create your views here.

@login_required
def workercalender(request):
    user_group = request.user.groups.values_list('name', flat=True)
    user_group = str(user_group[0])
    other = '''<a href="/viewothermonth"><button class='btn btn-secondary'>View another month</button></a>'''
    today = datetime.today()
    mounth = monthword(today.month)
    mperf = monthrange(today.year, today.month)
    userid = request.user.id
    if len(str(today.month)) == 1:
        mo = '-0' + str(today.month) + '-'
    else:
        mo = '-' + str(today.month) + '-'
    shifts = Shift.objects.filter(staff_id=userid, shift_date__contains=mo).exclude(status_code='Cancelled')
    calender = makecalender(mperf, shifts, mounth, today.year)
    return render(request, "info/workerpages/calender.html", {'calender': calender, 'other': other, 'usertype': user_group})

@login_required
def viewother(request):
    user_group = request.user.groups.values_list('name', flat=True)
    user_group = str(user_group[0])
    if request.method == "POST":
        year = request.POST['year']
        month = request.POST['month']
        if month == '':
           messages.success(request, 'Please select a month.', extra_tags='error')
           return redirect('/viewothermonth')
        other = '''<a href="/viewothermonth"><button class='btn btn-secondary'>View another month</button></a>'''
        mounth = monthword(month)
        mperf = monthrange(int(year), int(month))
        userid = request.user.id
        if len(str(month)) == 1:
            mo = str(year) + '-0' + str(month) + '-'
        else:
            mo = str(year) + '-' + str(month) + '-'
        shifts = Shift.objects.filter(staff_id=userid, shift_date__contains=mo).exclude(status_code='Cancelled')
        calender = makecalender(mperf, shifts, mounth, year)
        return render(request, "info/workerpages/calender.html", {'calender': calender, 'other': other, 'usertype': user_group})
    dates = ['Error'] * 30
    today = date.today()
    count = 0
    year = int(today.year)
    for i in range(30):
        dates[count] = year
        count += 1
        year -= 1
    return render(request, "info/workerpages/viewothermonth.html", {'year': dates, 'usertype': user_group})

@login_required
@allowed_users1(allowed_roles=['Coordinator', 'Bookeeper', 'Worker', 'Supervisor'])
def shiftdetails(request):
    user_group = request.user.groups.values_list('name', flat=True)
    user_group = str(user_group[0])
    userid = request.user.id
    test = str(request)
    y = ''
    for x in test:
        if x.isnumeric():
            y = y + x
    shiftitems = Shift.objects.filter(shift_id=y)
    for i in shiftitems:
        staff = i.staff_id

    if str(staff) == str(userid):
        for i in shiftitems:
            client = i.client_id
            department = i.dep_code
            status = i.status_code
            day = i.shift_date
            hourstart = i.scheduled_start
            hourend = i.scheduled_end
            supervisor = i.shift_super
            notes = i.shift_notes
        fname = Client.objects.filter(client_id=client).values_list('client_fname', flat=True)
        lname = Client.objects.filter(client_id=client).values_list('client_lname', flat=True)
        name = str(fname[0]) + ', ' + str(lname[0])
        depart = department.dep_name
        time = str(hourstart) + '-' + str(hourend)
    else:
        messages.success(request, 'Shift Error. your not registered for this shift. If you think this is a system error contact a administrator.', extra_tags='error')
        return redirect('/viewothermonth')
    return render(request, "info/workerpages/viewshiftdetails.html", {'usertype': user_group, 'time': time, 'client': name, 'department': depart, 'status': status, 'day': day, 'supervisor': supervisor, 'notes': notes})

@login_required
def timesheet(request):
    user_group = request.user.groups.values_list('name', flat=True)
    user_group = str(user_group[0])

    check = 0
    bp = 0
    empty = 0
    if request.method == "POST":
        for i in request.POST:
            if check == 1:
                test = i.split("-")
                if str(test[0]) == bp:
                    userid = request.user.id
                    staffid = Shift.objects.filter(shift_id=bp).values_list('staff_id', flat=True)
                    if str(staffid[0]) == str(userid):
                        w = str(bp) + '-st'
                        e = str(bp) + '-en'
                        Shift.objects.filter(pk=bp).update(status_code='Claimed', claimed_start=request.POST[w], claimed_end=request.POST[e])
            test = i.split("-")
            if len(test) == 2:
                if str(test[1]) == 'st':
                    bp = test[0]
                    check = 1
                    continue
    userid = request.user.id
    today = datetime.today()
    ave = today.month - 1
    if int(today.day) <= 15:
        if ave == 12:
            year = today.year - 1
        else:
            year = today.year
        the = monthrange(int(year), (int(ave)))
        start = str(year) + '-' + str(ave) + '-' + '16'
        end = str(year) + '-' + str(ave) + '-' + str(the[1])
        uue = ave
    else:
        if ave == 12:
            year = today.year - 1
        else:
            year = today.year
        the = monthrange(int(year), int(today.month))
        start = str(year) + '-' + str(today.month) + '-' + '1'
        end = str(year) + '-' + str(today.month) + '-' + '15'
        uue = today.month
    shifts = Shift.objects.filter(staff_id=userid, status_code='Scheduled', shift_date__range=(start, end))
    fname = Profile.objects.filter(staff_id=userid).values_list('staff_fname', flat=True)
    lname = Profile.objects.filter(staff_id=userid).values_list('staff_lname', flat=True)
    name = str(fname[0]) + ', ' + str(lname[0])
    time = maketimesheet(shifts, today, the)
    if len(shifts) == 0:
        empty = 1
    return render(request, "info/workerpages/timesheet.html", {'usertype': user_group, 'empty': empty, 'name': name, 'month': uue, 'year': year, 'time': time})

@login_required
def altershift(request):

    user_group = request.user.groups.values_list('name', flat=True)
    user_group = str(user_group[0])

    if request.method == "POST":
        check = 0
        for i in request.POST:
            if check == 1:
                sfg = str(i).split('-')
                if sfg[0] == bp and sfg[1] == 'en':
                    Shift.objects.filter(pk=bp).update(status_code='Claimed', claimed_start=request.POST[str(bp + '-st')], claimed_end=request.POST[str(bp + '-en')])
                    check = 0
            shg = str(i).split('-')
            if len(shg) == 1:
                continue
            if shg[1] == 'st':
                if len(request.POST[i]) != 0:
                    check = 1
                    bp = shg[0]
    today = datetime.today()
    if today.day < 15:
        month = today.month - 1
        search = str(today.year) + '-' + str(month) + '-' + '15'
    else:
        month = today.month - 1
        num = monthrange(today.year - 1, today.month - 1)
        search = str(today.year) + '-' + str(month) + '-' + str(num[1])

    shifts = Shift.objects.filter(shift_date__range=["1900-01-01", search], status_code='Scheduled')
    return render(request, "schedule/altershift.html", {'usertype': user_group, 'shift': shifts})




