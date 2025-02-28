import datetime
import django.utils.datastructures
from .forms import scedshiftform
from django.contrib.auth.decorators import login_required
import json
from info.decorators import allowed_users, allowed_users1
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.db.models import Max
from .function_roll import *


# Create your views here.

# Makes sure the users auth lvl is to the required lvl.
@login_required
@allowed_users(allowed_roles=['Coordinator', 'Bookeeper'])
def scedshift(request):
    user_group = request.user.groups.values_list('name', flat=True)
    user_group = str(user_group[0])

    # Defined variables.
    getdep = Department.objects.all()
    dropdown_varibles = Client.objects.all().values_list('client_id', 'client_fname', 'client_lname')
    dropdown_varibles1 = Profile.objects.all()
    dropdown_varibles2 = Profile.objects.filter(type_code='Worker').values_list('staff_id', 'staff_fname', 'staff_lname')
    dropdown = ['Error'] * len(dropdown_varibles)
    dropdownst = ['Error'] * len(dropdown_varibles2)
    counter = 0
    counter2 = 0
    error = 0
    shiftdatae = ''
    shiftstart = ''
    shiftend = ''
    cliid = ''
    today = date.today()
    recshift = ''
    supernum = ''
    shiftnotes = ''
    depart = ''
    avalablestaff = ''
    # Making a dropdown with all clients
    for i in dropdown_varibles:
        dropdown[counter] = 'CID(' + str(i[0]) + ')' + ' ' + i[1] + ', ' + i[2]
        counter += 1
    dropdown = json.dumps(list(dropdown))
    for i in dropdown_varibles2:
        dropdownst[counter2] = 'ID(' + str(i[0]) + ')' + ' ' + i[1] + ', ' + i[2]
        counter2 += 1
    dropdown2 = json.dumps(list(dropdownst))
    if request.method == "POST":
        form = scedshiftform(request.POST)
        # If the user presses the button to find avalible staff this route is used.
        if 'getstaff' in request.POST['submit']:
            if form:
                # setting variables to avoid errors.
                dateerror = 0
                starterror = 0
                enderror = 0
                shiftdatae = ''
                shiftstart = ''
                shiftend = ''
                form.full_clean()
                recshift = form.cleaned_data["rec_shift"]
                supernum = form.cleaned_data["shift_super"]
                # The form is not verified due to this search requiring only 3 variables, Another form cloud be created
                # but this is quicker and will return fewer errors. These trys make sure the variables are set and
                # returns an error if not.
                try:
                    clientname = str(form.cleaned_data["client_id"])
                except KeyError:
                    clientname = ''
                try:
                    shiftnotes = form.cleaned_data["shift_notes"]
                except KeyError:
                    shiftnotes = ""
                try:
                    depart = form.cleaned_data["dep_code"]
                except KeyError:
                    depart = ""
                try:
                    cliid = form.cleaned_data["client_id"]
                except KeyError:
                    cliid = ""
                try:
                    shiftdatae = form.cleaned_data["shift_date"]
                    shiftdate = str(shiftdatae).split("-")
                except KeyError as e:
                    error += 1
                    dateerror = 1
                try:
                    shiftstart = form.cleaned_data["scheduled_start"]
                except KeyError as e:
                    error += 1
                    starterror = 1
                try:
                    shiftend = form.cleaned_data["scheduled_end"]
                except KeyError as e:
                    error += 1
                    enderror = 1
                # If there is an error a message is returned.
                if error > 0:
                    if dateerror == 1:
                        shiftdatae = ''
                    if starterror == 1:
                        shiftstart = ''
                    if enderror == 1:
                        shiftend = ''
                    form = scedshiftform(initial={'shift_date': shiftdatae, 'scheduled_start': shiftstart,
                                                  'scheduled_end': shiftend, 'client_id': clientname,
                                                  'rec_shift': recshift,
                                                  'shift_super': supernum, 'shift_notes': shiftnotes})
                    # This gets the department and returns nothing if nothing was set.
                    try:
                        quryval = Department.objects.filter(dep_code=depart).values_list('dep_name', flat=True)
                        progval = 'value=' + str(depart)
                        progval1 = str(quryval[0])
                    except IndexError:
                        progval = 'value='
                        progval1 = 'Select a Department:'
                    messages.warning(request, 'Make sure the Date, start time, and end time are filled out ',
                                     extra_tags='mor')
                    return render(request, 'schedule/schedshift.html',
                                  {'staffis': 1, 'form': form, 'dep': getdep, 'dropdown': dropdown,
                                   'dropdown1': dropdown_varibles1,
                                   'state': False, 'startval': progval, 'startval1': progval1, 'dropdown2': dropdown2, 'usertype': user_group})
                shiftday = datetime(int(shiftdate[0]), int(shiftdate[1]), int(shiftdate[2])).weekday()
                dayofweek = {0: 'mon_avail', 1: 'tue_avail', 2: 'wed_avail', 3: 'thu_avail', 4: 'fri_avail',
                             5: 'sat_avail', 6: 'sun_avail', }
                query = getdayofweek(shiftday)
                stafflist = query.values_list(dayofweek[shiftday], 'staff_id', 'staff_fname', 'staff_lname')
                count = 0
                # This finds avalible staff based on time and date
                avalablestaff = [''] * len(stafflist)
                for i in stafflist:
                    timelist = str(i[0]).split(' - ')
                    start = str(timelist[0]).split(':')
                    start = datetime.time(int(start[0]), int(start[1]))
                    end = str(timelist[1]).split(':')
                    end = datetime.time(int(end[0]), int(end[1]))
                    if shiftstart.hour <= start.hour and shiftend.hour >= end.hour:
                        avalablestaff[count] = [i[1], i[2], i[3]]
                        count += 1
            form = scedshiftform(initial={'shift_date': shiftdatae, 'scheduled_start': shiftstart,
                                          'scheduled_end': shiftend, 'client_id': cliid, 'rec_shift': recshift,
                                          'shift_super': supernum, 'shift_notes': shiftnotes})
            deparmenv = getdepartment(depart)
            # This will return an error message if there are no staff with the required specs.
            if not avalablestaff:
                messages.warning(request, 'No avalable staff for the given date/time', extra_tags='mor')
            return render(request, 'schedule/schedshift.html',
                          {'staffis': 0, 'form': form, 'dep': getdep, 'dropdown': dropdown, 'dropdown1': avalablestaff,
                           'state': False, 'startval1': deparmenv[1], 'startval': deparmenv[0], 'dropdown2': dropdown2, 'usertype': user_group})
        # If the user presses submit this route is taken.
        if 'make' or 'make1' in request.POST['submit']:
            if form.is_valid():
                form.full_clean()
                # Declaring variables and reworking data into differant forms.
                clientname = str(form.cleaned_data["client_id"])
                cleaned = str(form.cleaned_data["client_id"]).split(' ')
                cleaned = cleaned[0].replace('CID(', '').replace(')', '')
                staffnum = form.cleaned_data["staff_id"]
                cleanedstaff = str(form.cleaned_data["staff_id"]).split(' ')
                staffid = cleanedstaff[0].replace('ID(', '').replace(')', '')
                recshift = form.cleaned_data["rec_shift"]
                supernum = form.cleaned_data["shift_super"]
                shiftnotes = form.cleaned_data["shift_notes"]
                clendepart = form.cleaned_data["dep_code"]
                depart = Department.objects.get(dep_code=form.cleaned_data["dep_code"])
                cliid = Client.objects.get(client_id=cleaned)
                shiftdatae = form.cleaned_data["shift_date"]
                shiftstart = form.cleaned_data["scheduled_start"]
                shiftend = form.cleaned_data["scheduled_end"]
                staff = Profile.objects.get(staff_id=staffid)
                # See function_roll.py for erroring the inputs
                print(today)
                print(request.POST['shift_date'])
                if request.POST['shift_date'] < str(today):
                    form = scedshiftform(initial={'shift_date': shiftdatae, 'scheduled_start': shiftstart,
                                                  'scheduled_end': shiftend, 'client_id': clientname,
                                                  'rec_shift': recshift,
                                                  'shift_super': supernum, 'shift_notes': shiftnotes})
                    deparmenv = getdepartment(clendepart)
                    staffreturn = getstaff(staffid)
                    messages.warning(request, 'The start date must be after the current date.',
                                     extra_tags='error')
                    return render(request, "schedule/schedshift.html",
                                  {'staffis': 1, 'form': form, 'dep': getdep, 'dropdown': dropdown,
                                   'dropdown1': dropdown_varibles1,
                                   'state': True, 'startval1': deparmenv[1], 'startval': deparmenv[0],
                                   'staffval': staffreturn[0], 'staffval1': staffreturn[1], 'dropdown2': dropdown2, 'usertype': user_group})
                if recshift:
                    # if the shift need to be recurring.
                    rec_end = request.POST.get('rec-time')
                    byletter = thorsday(shiftdatae, rec_end)
                    if byletter:
                        form = scedshiftform(initial={'shift_date': shiftdatae, 'scheduled_start': shiftstart,
                                                      'scheduled_end': shiftend, 'client_id': clientname,
                                                      'rec_shift': recshift,
                                                      'shift_super': supernum, 'shift_notes': shiftnotes})
                        deparmenv = getdepartment(clendepart)
                        staffreturn = getstaff(staffid)
                        messages.success(request,
                                         'Rec shifts need to start and end on the same day of the week',
                                         extra_tags='error')
                        return render(request, "schedule/schedshift.html",
                                      {'staffis': 1, 'form': form, 'dep': getdep, 'dropdown': dropdown,
                                       'dropdown1': dropdown_varibles1,
                                       'state': True, 'startval1': deparmenv[1], 'startval': deparmenv[0],
                                       'staffval': staffreturn[0], 'staffval1': staffreturn[1], 'recin': recshift,
                                       'enddatte': rec_end, 'dropdown2': dropdown2, 'usertype': user_group})
                    conflicdates = befores(shiftdatae, rec_end)
                    if conflicdates:
                        form = scedshiftform(initial={'shift_date': shiftdatae, 'scheduled_start': shiftstart,
                                                      'scheduled_end': shiftend, 'client_id': clientname,
                                                      'rec_shift': recshift,
                                                      'shift_super': supernum, 'shift_notes': shiftnotes})
                        deparmenv = getdepartment(clendepart)
                        staffreturn = getstaff(staffid)
                        messages.success(request,
                                         'The end date needs to be after the start',
                                         extra_tags='error')
                        return render(request, "schedule/schedshift.html",
                                      {'staffis': 1, 'form': form, 'dep': getdep, 'dropdown': dropdown,
                                       'dropdown1': dropdown_varibles1,
                                       'state': True, 'startval1': deparmenv[1], 'startval': deparmenv[0],
                                       'staffval': staffreturn[0], 'staffval1': staffreturn[1], 'recin': recshift,
                                       'enddatte': rec_end, 'dropdown2': dropdown2, 'usertype': user_group})
                if shiftstart > shiftend:
                    form = scedshiftform(initial={'shift_date': shiftdatae, 'scheduled_start': shiftstart,
                                                  'scheduled_end': shiftend, 'client_id': clientname,
                                                  'rec_shift': recshift,
                                                  'shift_super': supernum, 'shift_notes': shiftnotes})
                    deparmenv = getdepartment(clendepart)
                    staffreturn = getstaff(staffid)
                    messages.warning(request, 'The start time must be before the end time.',
                                     extra_tags='error')
                    return render(request, "schedule/schedshift.html",
                                  {'staffis': 1, 'form': form, 'dep': getdep, 'dropdown': dropdown,
                                   'dropdown1': dropdown_varibles1,
                                   'state': True, 'startval1': deparmenv[1], 'startval': deparmenv[0],
                                   'staffval': staffreturn[0], 'staffval1': staffreturn[1], 'dropdown2': dropdown2, 'usertype': user_group})
                if recshift:
                    # if the shift need to be recurring.
                    rec_end = request.POST.get('rec-time')
                    byletter = thorsday(shiftdatae, rec_end)
                    if byletter:
                        form = scedshiftform(initial={'shift_date': shiftdatae, 'scheduled_start': shiftstart,
                                                      'scheduled_end': shiftend, 'client_id': clientname,
                                                      'rec_shift': recshift,
                                                      'shift_super': supernum, 'shift_notes': shiftnotes})
                        deparmenv = getdepartment(clendepart)
                        staffreturn = getstaff(staffid)
                        messages.success(request,
                                         'Rec shifts need to start and end on the same day of the week',
                                         extra_tags='error')
                        return render(request, "schedule/schedshift.html",
                                      {'staffis': 1, 'form': form, 'dep': getdep, 'dropdown': dropdown,
                                       'dropdown1': dropdown_varibles1,
                                       'state': True, 'startval1': deparmenv[1], 'startval': deparmenv[0],
                                       'staffval': staffreturn[0], 'staffval1': staffreturn[1], 'recin': recshift,
                                       'enddatte': rec_end, 'dropdown2': dropdown2, 'usertype': user_group})
                    conflicdates = befores(shiftdatae, rec_end)
                    if conflicdates:
                        form = scedshiftform(initial={'shift_date': shiftdatae, 'scheduled_start': shiftstart,
                                                      'scheduled_end': shiftend, 'client_id': clientname,
                                                      'rec_shift': recshift,
                                                      'shift_super': supernum, 'shift_notes': shiftnotes})
                        deparmenv = getdepartment(clendepart)
                        staffreturn = getstaff(staffid)
                        messages.success(request,
                                         'The end date needs to be after the start',
                                         extra_tags='error')
                        return render(request, "schedule/schedshift.html",
                                      {'staffis': 1, 'form': form, 'dep': getdep, 'dropdown': dropdown,
                                       'dropdown1': dropdown_varibles1,
                                       'state': True, 'startval1': deparmenv[1], 'startval': deparmenv[0],
                                       'staffval': staffreturn[0], 'staffval1': staffreturn[1], 'recin': recshift,
                                       'enddatte': rec_end, 'dropdown2': dropdown2, 'usertype': user_group})
                    shiftlist = recshiftdays(shiftdatae, rec_end)
                    rec_day = letterday(shiftdatae.weekday())
                    recid = RecShift.objects.aggregate(Max('rec_id'))
                    recover = rechours(shiftlist, cleaned, shiftstart, shiftend)
                    if len(recover) != 0:
                        form = scedshiftform(initial={'shift_date': shiftdatae, 'scheduled_start': shiftstart,
                                                      'scheduled_end': shiftend, 'client_id': clientname,
                                                      'rec_shift': recshift,
                                                      'shift_super': supernum, 'shift_notes': shiftnotes})
                        deparmenv = getdepartment(clendepart)
                        staffreturn = getstaff(staffid)
                        messages.warning(request, f'The Client is going over max hours for the months of ({recover})',
                                         extra_tags='error')
                        return render(request, "schedule/schedshift.html",
                                      {'staffis': 1, 'form': form, 'dep': getdep, 'dropdown': dropdown,
                                       'dropdown1': dropdown_varibles1,
                                       'state': True, 'startval1': deparmenv[1], 'startval': deparmenv[0],
                                       'staffval': staffreturn[0], 'staffval1': staffreturn[1], 'recin': recshift,
                                       'enddatte': rec_end, 'dropdown2': dropdown2, 'usertype': user_group})
                    recconflict = recintersection(shiftlist, cleaned, staffid, shiftstart, shiftend, '')
                    if recconflict[0]:
                        form = scedshiftform(initial={'shift_date': shiftdatae, 'scheduled_start': shiftstart,
                                                      'scheduled_end': shiftend, 'client_id': clientname,
                                                      'rec_shift': recshift,
                                                      'shift_super': supernum, 'shift_notes': shiftnotes})
                        deparmenv = getdepartment(clendepart)
                        staffreturn = getstaff(staffid)
                        messages.warning(request, recconflict[1], extra_tags='error')
                        return render(request, "schedule/schedshift.html",
                                      {'staffis': 1, 'form': form, 'dep': getdep, 'dropdown': dropdown,
                                       'dropdown1': dropdown_varibles1,
                                       'state': True, 'startval1': deparmenv[1], 'startval': deparmenv[0],
                                       'staffval': staffreturn[0], 'staffval1': staffreturn[1], 'recin': recshift,
                                       'enddatte': rec_end, 'dropdown2': dropdown2, 'usertype': user_group})
                    rectimeover = recovertime(staffnum, shiftlist, shiftstart, shiftend, request.POST['submit'])
                    if rectimeover[0]:
                        form = scedshiftform(initial={'shift_date': shiftdatae, 'scheduled_start': shiftstart,
                                                      'scheduled_end': shiftend, 'client_id': clientname,
                                                      'rec_shift': recshift,
                                                      'shift_super': supernum, 'shift_notes': shiftnotes})
                        deparmenv = getdepartment(clendepart)
                        staffreturn = getstaff(staffid)
                        messages.warning(request, f'The worker will work overtime for {rectimeover[1]} shifts',
                                         extra_tags='error')
                        return render(request, "schedule/schedshift.html",
                                      {'staffis': 1, 'form': form, 'dep': getdep, 'dropdown': dropdown,
                                       'dropdown1': dropdown_varibles1,
                                       'state': True, 'startval1': deparmenv[1], 'startval': deparmenv[0],
                                       'staffval': staffreturn[0], 'staffval1': staffreturn[1], 'overtime': 1,
                                       'recin': recshift, 'enddatte': rec_end, 'dropdown2': dropdown2, 'usertype': user_group})
                    if recid['rec_id__max'] is not None:
                        recid = int(recid['rec_id__max']) + 1
                    else:
                        recid = 1
                    r = RecShift(rec_start=shiftstart, rec_id=recid, dep_code=depart, client=cliid, staff=staff,
                                 rec_day=rec_day, rec_end=shiftend, rec_super=supernum, rec_notes=shiftnotes)
                    r.save()
                    for i in shiftlist:
                        o = Shift(rec_id=recid, status_code='Scheduled', client=cliid, dep_code=depart, shift_date=i,
                                  scheduled_start=shiftstart, scheduled_end=shiftend, shift_super=supernum,
                                  shift_notes=shiftnotes, staff=staff)
                        o.save()
                    messages.success(request,
                                     f'Added Shifts from {shiftdatae} to {rec_end} From {shiftstart} To {shiftend} Sucsessfully',
                                     extra_tags='submit')
                    return redirect('/scheduleshift')

                else:
                    # For single shifts
                    # See function_roll.py for error information.
                    clienthavehours = clienthours(shiftdatae, cleaned, shiftstart, shiftend)
                    if clienthavehours[0]:
                        form = scedshiftform(initial={'shift_date': shiftdatae, 'scheduled_start': shiftstart,
                                                      'scheduled_end': shiftend, 'client_id': clientname,
                                                      'rec_shift': recshift,
                                                      'shift_super': supernum, 'shift_notes': shiftnotes})
                        deparmenv = getdepartment(clendepart)
                        staffreturn = getstaff(staffid)
                        messages.success(request,
                                         f'Client {clientname} has reached max hours.(max hours={clienthavehours[1]}), (total hours scheduled={clienthavehours[2]}))',
                                         extra_tags='error')
                        return render(request, "schedule/schedshift.html",
                                      {'staffis': 1, 'form': form, 'dep': getdep, 'dropdown': dropdown,
                                       'dropdown1': dropdown_varibles1,
                                       'state': True, 'startval1': deparmenv[1], 'startval': deparmenv[0],
                                       'staffval': staffreturn[0], 'staffval1': staffreturn[1], 'dropdown2': dropdown2, 'usertype': user_group})
                    intersectshifts = intersect(shiftdatae, shiftstart, shiftend, cleaned, staffnum, '')
                    if intersectshifts[0]:
                        form = scedshiftform(initial={'shift_date': shiftdatae, 'scheduled_start': shiftstart,
                                                      'scheduled_end': shiftend, 'client_id': clientname,
                                                      'rec_shift': recshift,
                                                      'shift_super': supernum, 'shift_notes': shiftnotes})
                        deparmenv = getdepartment(clendepart)
                        staffreturn = getstaff(staffid)
                        messages.success(request,
                                         f'Shift intersects with another shift the {intersectshifts[1]} is scheduled for',
                                         extra_tags='error')
                        return render(request, "schedule/schedshift.html",
                                      {'staffis': 1, 'form': form, 'dep': getdep, 'dropdown': dropdown,
                                       'dropdown1': dropdown_varibles1,
                                       'state': True, 'startval1': deparmenv[1], 'startval': deparmenv[0],
                                       'staffval': staffreturn[0], 'staffval1': staffreturn[1], 'dropdown2': dropdown2, 'usertype': user_group})
                    overtime = shiftovertime(staffid, shiftdatae, shiftstart, shiftend, request.POST['submit'])
                    if overtime:
                        form = scedshiftform(initial={'shift_date': shiftdatae, 'scheduled_start': shiftstart,
                                                      'scheduled_end': shiftend, 'client_id': clientname,
                                                      'rec_shift': recshift,
                                                      'shift_super': supernum, 'shift_notes': shiftnotes})

                        deparmenv = getdepartment(clendepart)
                        staffreturn = getstaff(staffid)
                        messages.success(request,
                                         'Staff is going into overtime hours.',
                                         extra_tags='error')
                        return render(request, "schedule/schedshift.html",
                                      {'staffis': 1, 'form': form, 'dep': getdep, 'dropdown': dropdown,
                                       'dropdown1': dropdown_varibles1,
                                       'state': True, 'startval1': deparmenv[1], 'startval': deparmenv[0],
                                       'overtime': 1, 'staffval': staffreturn[0], 'staffval1': staffreturn[1],
                                       'dropdown2': dropdown2, 'usertype': user_group})

                    t = Shift(status_code='Scheduled', client=cliid, dep_code=depart, shift_date=shiftdatae,
                              scheduled_start=shiftstart, scheduled_end=shiftend, shift_super=supernum,
                              shift_notes=shiftnotes, staff=staff)
                    t.save()
                    messages.success(request,
                                     f'Added Shift On {shiftdatae} From {shiftstart} To {shiftend} Sucsessfully',
                                     extra_tags='submit')
                    return redirect('/scheduleshift')

        else:
            return redirect('/land')

    else:
        # returns an empty form.
        form = scedshiftform()
        progval = 'value='
        progval1 = 'Select a Department:'
        stval = 'value='
        stval1 = 'Select a Staff Member:'
        return render(request, "schedule/schedshift.html",
                      {'staffis': 1, 'form': form, 'dep': getdep, 'dropdown': dropdown, 'dropdown1': dropdown_varibles1,
                       'state': True, 'startval1': progval1, 'startval': progval, 'staffval': stval,
                       'staffval1': stval1, 'dropdown2': dropdown2, 'usertype': user_group})

@login_required
@allowed_users(allowed_roles=['Coordinator', 'Bookeeper'])
def viewshift(request):
    if request.user.is_authenticated:
        user_group = request.user.groups.values_list('name', flat=True)
        user_group = str(user_group[0])
    else:
        return redirect('/login')
    if request.method == "POST":
        if not request.POST['month']:
            messages.success(request, 'Please enter a month', extra_tags='error')
            return redirect('/viewshift')
        if not request.POST['impotsh']:
            messages.success(request, 'Please select an option', extra_tags='error')
            return redirect('/viewshift')
        switch = request.POST['impotsh']
        year = request.POST['year']
        month = request.POST['month']
        montth = monthword(month)
        if request.POST['impotsh'] == 's':
            if not request.POST['searchstaff']:
                if not request.POST['searchstaffselect']:
                    messages.success(request, 'Please enter a staff member', extra_tags='error')
                    return redirect('/viewshift')
            if not request.POST['searchstaff']:
                id = request.POST['searchstaffselect']
                need_list = shiftrender(switch, year, month, id)
                return render(request, "schedule/veiwscedshift.html",
                              {'list': need_list, 'year': year, 'month': montth})
            id = request.POST['searchstaff']
            need_list = shiftrender(switch, year, month, id)
            return render(request, "schedule/veiwscedshift.html", {'usertype': user_group, 'list': need_list, 'year': year, 'month': montth})

        elif request.POST['impotsh'] == 'c':
            if not request.POST['searchclient']:
                if not request.POST['searchclientselect']:
                    messages.success(request, 'Please enter a client', extra_tags='error')
                    return redirect('/viewshift')
            if not request.POST['searchclient']:
                id = request.POST['searchclientselect']
                need_list = shiftrender(switch, year, month, id)
                return render(request, "schedule/veiwscedshift.html",
                              {'list': need_list, 'year': year, 'month': montth})
            id = request.POST['searchclient']
            need_list = shiftrender(switch, year, month, id)
            return render(request, "schedule/veiwscedshift.html", {'usertype': user_group, 'list': need_list, 'year': year, 'month': montth})

        elif request.POST['impotsh'] == 'd':
            if not request.POST['searchdep']:
                if not request.POST['searchdepselect']:
                    messages.success(request, 'Please enter a department', extra_tags='eviewscedulerror')
                    return redirect('/viewshift')
            if not request.POST['searchdep']:
                id = request.POST['searchdepselect']
                need_list = shiftrender(switch, year, month, id)
                return render(request, "schedule/veiwscedshift.html",
                              {'list': need_list, 'year': year, 'month': montth, 'usertype': user_group})
            id = request.POST['searchdep']
            need_list = shiftrender(switch, year, month, id)
            return render(request, "schedule/veiwscedshift.html", {'usertype': user_group, 'list': need_list, 'year': year, 'month': montth})
    staff = Profile.objects.filter(type_code='Worker').values_list('staff_id', 'staff_fname', 'staff_lname')
    client = Client.objects.values_list('client_id', 'client_fname', 'client_lname')
    department = Department.objects.values_list('dep_name', 'dep_code')
    stafflist = ['Error'] * len(staff)
    staffid = ['Error'] * len(staff)
    clientlist = ['Error'] * len(client)
    clientid = ['Error'] * len(client)
    deplist = ['Error'] * len(department)
    depid = ['Error'] * len(department)
    depview = ['Error'] * len(department)
    count = 0
    for i in department:
        deplist[count] = i[0]
        depid[count] = i[1]
        depview[count] = '(' + str(i[1]) + ') ' + str(i[0])
        count += 1

    department = zip(deplist, depid)
    count = 0

    for i in staff:
        val = 'ID(' + str(i[0]) + ') ' + str(i[1]) + ', ' + str(i[2])
        stafflist[count] = val
        staffid[count] = i[0]
        count += 1

    stafflist1 = zip(stafflist, staffid)
    count = 0

    for i in client:
        val = 'CID(' + str(i[0]) + ') ' + str(i[1]) + ', ' + str(i[2])
        clientlist[count] = val
        clientid[count] = i[0]
        count += 1

    clientlist1 = zip(clientlist, clientid)

    dates = ['Error'] * 30
    today = date.today()
    count = 0
    year = int(today.year)
    for i in range(30):
        dates[count] = year
        count += 1
        year -= 1
    deplistit = json.dumps(list(deplist))
    stafflistit = json.dumps(list(stafflist))
    clientlistit = json.dumps(list(clientlist))
    return render(request, "schedule/viewshift.html",
                  {'Staff': stafflist1, 'Client': clientlist1, 'Department': department, 'year': dates,
                   'staffit': stafflistit, 'clientit': clientlistit, 'depit':deplistit, 'dview': depview, 'usertype': user_group})

@login_required
@allowed_users1(allowed_roles=['Coordinator', 'Bookeeper'])
def modshift(request):
    user_group = request.user.groups.values_list('name', flat=True)
    user_group = str(user_group[0])

    error = 0
    overtime = 0
    err = 0
    counter = 0
    counter2 = 0
    getdep = Department.objects.all()
    dropdown_varibles = Client.objects.all().values_list('client_id', 'client_fname', 'client_lname')
    dropdown_varibles1 = Profile.objects.all()
    dropdown_varibles2 = Profile.objects.filter(type_code='Worker').values_list('staff_id', 'staff_fname', 'staff_lname')
    dropdown = ['Error'] * len(dropdown_varibles)
    dropdownst = ['Error'] * len(dropdown_varibles2)
    for i in dropdown_varibles:
        dropdown[counter] = 'CID(' + str(i[0]) + ')' + ' ' + i[1] + ', ' + i[2]
        counter += 1
    dropdown = json.dumps(list(dropdown))
    for i in dropdown_varibles2:
        dropdownst[counter2] = 'ID(' + str(i[0]) + ')' + ' ' + i[1] + ', ' + i[2]
        counter2 += 1
    dropdown2 = json.dumps(list(dropdownst))
    test = str(request)
    y = ''
    for x in test:
        if x.isnumeric():
            y = y + x
    shiftinfo = Shift.objects.filter(shift_id=y)
    if request.method == "POST":
        form = scedshiftform(request.POST)
        if 'getstaff' in request.POST['submit']:
            if form:
                # setting variables to avoid errors.
                code = request.POST['status']
                dateerror = 0
                starterror = 0
                enderror = 0
                shiftdatae = ''
                shiftstart = ''
                shiftend = ''
                form.full_clean()
                recshift = form.cleaned_data["rec_shift"]
                supernum = form.cleaned_data["shift_super"]
                # The form is not verified due to this search requiring only 3 variables, Another form cloud be created
                # but this is quicker and will return fewer errors. These trys make sure the variables are set and
                # returns an error if not.
                try:
                    clientname = str(form.cleaned_data["client_id"])
                except KeyError:
                    clientname = ''
                try:
                    shiftnotes = form.cleaned_data["shift_notes"]
                except KeyError:
                    shiftnotes = ""
                try:
                    depart = form.cleaned_data["dep_code"]
                except KeyError:
                    depart = ""
                try:
                    cliid = form.cleaned_data["client_id"]
                except KeyError:
                    cliid = ""
                try:
                    shiftdatae = form.cleaned_data["shift_date"]
                    shiftdate = str(shiftdatae).split("-")
                except KeyError as e:
                    error += 1
                    dateerror = 1
                try:
                    shiftstart = form.cleaned_data["scheduled_start"]
                except KeyError as e:
                    error += 1
                    starterror = 1
                try:
                    shiftend = form.cleaned_data["scheduled_end"]
                except KeyError as e:
                    error += 1
                    enderror = 1
                # If there is an error a message is returned.
                if error > 0:
                    if dateerror == 1:
                        shiftdatae = ''
                    if starterror == 1:
                        shiftstart = ''
                    if enderror == 1:
                        shiftend = ''
                    form = scedshiftform(initial={'shift_date': shiftdatae, 'scheduled_start': shiftstart,
                                                  'scheduled_end': shiftend, 'client_id': clientname,
                                                  'shift_super': supernum, 'shift_notes': shiftnotes, 'status': code})
                    # This gets the department and returns nothing if nothing was set.
                    try:
                        quryval = Department.objects.filter(dep_code=depart).values_list('dep_name', flat=True)
                        progval = 'value=' + str(depart)
                        progval1 = str(quryval[0])
                    except IndexError:
                        progval = 'value='
                        progval1 = 'Select a Department:'
                    messages.warning(request, 'Make sure the Date, start time, and end time are filled out ',
                                     extra_tags='mor')
                    return render(request, 'schedule/modshift.html',
                                  {'staffis': 1, 'form': form, 'dep': getdep, 'dropdown': dropdown,
                                   'dropdown1': dropdown_varibles1,
                                   'state': False, 'startval': progval, 'startval1': progval1, 'dropdown2': dropdown2,
                                   'status': code, 'usertype': user_group})
                shiftday = datetime(int(shiftdate[0]), int(shiftdate[1]), int(shiftdate[2])).weekday()
                dayofweek = {0: 'mon_avail', 1: 'tue_avail', 2: 'wed_avail', 3: 'thu_avail', 4: 'fri_avail',
                             5: 'sat_avail', 6: 'sun_avail', }
                query = getdayofweek(shiftday)
                stafflist = query.values_list(dayofweek[shiftday], 'staff_id', 'staff_fname', 'staff_lname')
                count = 0
                # This finds avalible staff based on time and date
                avalablestaff = [''] * len(stafflist)
                for i in stafflist:
                    timelist = str(i[0]).split(' - ')
                    start = str(timelist[0]).split(':')
                    start = datetime.time(int(start[0]), int(start[1]))
                    end = str(timelist[1]).split(':')
                    end = datetime.time(int(end[0]), int(end[1]))
                    if shiftstart.hour <= start.hour and shiftend.hour >= end.hour:
                        avalablestaff[count] = [i[1], i[2], i[3]]
                        count += 1
            form = scedshiftform(initial={'shift_date': shiftdatae, 'scheduled_start': shiftstart,
                                          'scheduled_end': shiftend, 'client_id': cliid,
                                          'shift_super': supernum, 'shift_notes': shiftnotes})
            deparmenv = getdepartment(depart)
            # This will return an error message if there are no staff with the required specs.
            if not avalablestaff:
                messages.warning(request, 'No avalable staff for the given date/time', extra_tags='mor')
            return render(request, 'schedule/modshift.html',
                          {'staffis': 0, 'form': form, 'dep': getdep, 'dropdown': dropdown, 'dropdown1': avalablestaff,
                           'state': False, 'startval1': deparmenv[1], 'startval': deparmenv[0], 'dropdown2': dropdown2,
                           'status': code, 'usertype': user_group})
        if form.is_valid() and 'make' in request.POST['submit']:
            form.full_clean()
            # Declaring variables and reworking data into differant forms.
            clientname = str(form.cleaned_data["client_id"])
            cleaned = str(form.cleaned_data["client_id"]).split(' ')
            cleaned = cleaned[0].replace('CID(', '').replace(')', '')
            staffnum = form.cleaned_data["staff_id"]
            cleanedstaff = str(form.cleaned_data["staff_id"]).split(' ')
            staffid = cleanedstaff[0].replace('ID(', '').replace(')', '')
            supernum = form.cleaned_data["shift_super"]
            shiftnotes = form.cleaned_data["shift_notes"]
            clendepart = form.cleaned_data["dep_code"]
            depart = Department.objects.get(dep_code=form.cleaned_data["dep_code"])
            cliid = Client.objects.get(client_id=cleaned)
            shiftdatae = form.cleaned_data["shift_date"]
            shiftstart = form.cleaned_data["scheduled_start"]
            shiftend = form.cleaned_data["scheduled_end"]
            staff = Profile.objects.get(staff_id=staffid)
            status = request.POST.get('status', False)

            overtime = shiftovertime(staffid, shiftdatae, shiftstart, shiftend, request.POST['submit'])
            if request.POST['submit'] == 'make1':
                False
            else:
                if overtime:
                    mesg = messages.success(request, 'Staff is going into overtime hours.', extra_tags='error')
                    err = 1
                    overtime = 1
            clienthavehours = clienthours(shiftdatae, cleaned, shiftstart, shiftend)
            if clienthavehours[0]:
                mesg = messages.success(request,
                                        f'Client {clientname} has reached max hours.(max hours={clienthavehours[1]}), (total hours scheduled={clienthavehours[2]}))',
                                        extra_tags='error')
                err = 1
            intersectshifts = intersect(shiftdatae, shiftstart, shiftend, cleaned, staffnum, y)
            if intersectshifts[0]:
                messages.success(request,
                                 f'Shift intersects with another shift the {intersectshifts[1]} is scheduled for',
                                 extra_tags='error')
                err = 1
            if err == 1:
                form = scedshiftform(initial={'shift_date': shiftdatae, 'scheduled_start': shiftstart,
                                              'scheduled_end': shiftend, 'client_id': clientname,
                                              'shift_super': supernum, 'shift_notes': shiftnotes})
                deparmenv = getdepartment(clendepart)
                staffreturn = getstaff(staffid)
                mesg
                return render(request, "schedule/schedshift.html",
                              {'staffis': 1, 'form': form, 'dep': getdep, 'dropdown': dropdown,
                               'dropdown1': dropdown_varibles1,
                               'state': True, 'startval1': deparmenv[1], 'startval': deparmenv[0],
                               'staffval': staffreturn[0], 'staffval1': staffreturn[1], 'dropdown2': dropdown2,
                               'overtime': overtime, 'usertype': user_group})

            Shift.objects.filter(pk=y).update(client_id=cleaned, status_code=status, dep_code=depart,
                                              shift_date=shiftdatae,
                                              scheduled_start=shiftstart, scheduled_end=shiftend, staff_id=staff,
                                              shift_super=supernum, shift_notes=shiftnotes)
            messages.success(request, 'Shift record updated', extra_tags='submit')
            return redirect('/viewshift')

    else:
        for i in shiftinfo:
            cli = getclient(i.client_id)
            form = scedshiftform(
                initial={'client_id': cli,
                         'shift_date': i.shift_date, 'scheduled_start': i.scheduled_start,
                         'scheduled_end': i.scheduled_end, 'shift_super': i.shift_super,
                         'shift_notes': i.shift_notes})
            now = datetime.now()
            if now.date() >= i.shift_date and now.time() >= i.scheduled_start:
                messages.success(request, 'Shift is already past the start time no edits may be made',
                                 extra_tags='error')
                return redirect('/viewshift')
            valsuper = i.shift_super
            code = i.status_code
            staffreturn = getstaff(i.staff_id)
            redep = str(i.dep_code).replace('Department object (', '').replace(')', '')
            progval = getdepartment(redep)
            return render(request, "schedule/modshift.html",
                          {'usergroup': user_group, 'form': form, 'dropdown': dropdown, 'dropdown1': dropdown_varibles1,
                           'dropdown2': dropdown2, 'dep': getdep, 'staffis': 1, 'staffval': staffreturn[0],
                           'staffval1': staffreturn[1], 'startval': progval[0], 'startval1': progval[1], 'status': code,
                           'super': valsuper, 'usertype': user_group})

@login_required
@allowed_users(allowed_roles=['Coordinator', 'Bookeeper'])
def viewrecshifts(request):
    user_group = request.user.groups.values_list('name', flat=True)
    user_group = str(user_group[0])
    if request.method == "POST":
        if not request.POST['impotsh']:
            messages.success(request, 'Please select an option', extra_tags='error')
            return redirect('/viewrecshift')
        switch = request.POST['impotsh']
        if request.POST['impotsh'] == 's':
            if not request.POST['searchstaff']:
                if not request.POST['searchstaffselect']:
                    messages.success(request, 'Please enter a staff member', extra_tags='error')
                    return redirect('/viewrecshift')
            if not request.POST['searchstaff']:
                id = request.POST['searchstaffselect']
                need_list = shiftrenderrec(switch, id)
                return render(request, "schedule/viewrecscedshifts.html", {'list': need_list, 'for': request.POST['impotsh']})
            id = request.POST['searchstaff']
            need_list = shiftrenderrec(switch, id)
            return render(request, "schedule/viewrecscedshifts.html", {'list': need_list, 'for': request.POST['impotsh']})

        elif request.POST['impotsh'] == 'c':
            if not request.POST['searchclient']:
                if not request.POST['searchclientselect']:
                    messages.success(request, 'Please enter a client', extra_tags='error')
                    return redirect('/viewrecshift')
            if not request.POST['searchclient']:
                id = request.POST['searchclientselect']
                need_list = shiftrenderrec(switch, id)
                return render(request, "schedule/viewrecscedshifts.html", {'list': need_list, 'for': request.POST['impotsh']})
            id = request.POST['searchclient']
            need_list = shiftrenderrec(switch, id)
            return render(request, "schedule/viewrecscedshifts.html", {'list': need_list, 'for': request.POST['impotsh']})

        elif request.POST['impotsh'] == 'd':
            if not request.POST['searchdep']:
                if not request.POST['searchdepselect']:
                    messages.success(request, 'Please enter a department', extra_tags='error')
                    return redirect('/viewrecshift')
            if not request.POST['searchdep']:
                id = request.POST['searchdepselect']
                need_list = shiftrender(switch, id)
                return render(request, "schedule/viewrecscedshifts.html",
                              {'list': need_list, 'for': request.POST['impotsh']})
            id = request.POST['searchdep']
            need_list = shiftrender(switch, id)
            return render(request, "schedule/viewrecscedshifts.html", {'list': need_list, 'for': request.POST['impotsh']})
    staff = Profile.objects.filter(type_code='Worker').values_list('staff_id', 'staff_fname', 'staff_lname')
    client = Client.objects.values_list('client_id', 'client_fname', 'client_lname')
    department = Department.objects.values_list('dep_name', 'dep_code')
    stafflist = ['Error'] * len(staff)
    staffid = ['Error'] * len(staff)
    clientlist = ['Error'] * len(client)
    clientid = ['Error'] * len(client)
    deplist = ['Error'] * len(department)
    depid = ['Error'] * len(department)
    depview = ['Error'] * len(department)
    count = 0
    for i in department:
        deplist[count] = i[0]
        depid[count] = i[1]
        depview[count] = '(' + str(i[1]) + ') ' + str(i[0])
        count += 1

    department = zip(deplist, depid)
    count = 0

    for i in staff:
        val = 'ID(' + str(i[0]) + ') ' + str(i[1]) + ', ' + str(i[2])
        stafflist[count] = val
        staffid[count] = i[0]
        count += 1

    stafflist1 = zip(stafflist, staffid)
    count = 0

    for i in client:
        val = 'CID(' + str(i[0]) + ') ' + str(i[1]) + ', ' + str(i[2])
        clientlist[count] = val
        clientid[count] = i[0]
        count += 1

    clientlist1 = zip(clientlist, clientid)

    dates = ['Error'] * 30
    today = date.today()
    count = 0
    year = int(today.year)
    for i in range(30):
        dates[count] = year
        count += 1
        year -= 1
    deplistit = json.dumps(list(deplist))
    stafflistit = json.dumps(list(stafflist))
    clientlistit = json.dumps(list(clientlist))
    return render(request, "schedule/viewrecshift.html",
                  {'Staff': stafflist1, 'Client': clientlist1, 'depview': depview, 'Department': department, 'year': dates
                      , 'deplist': deplistit, 'clientlist': clientlistit, 'stafflist': stafflistit, 'usertype': user_group})

@login_required
@allowed_users1(allowed_roles=['Coordinator', 'Bookeeper'])
def modrecshift(request):
    user_group = request.user.groups.values_list('name', flat=True)
    user_group = str(user_group[0])

    msg = ''
    counter = 0
    counter2 = 0
    overtime = 0
    youerr = 0
    err = 0
    getdep = Department.objects.all()
    dropdown_varibles = Client.objects.all().values_list('client_id', 'client_fname', 'client_lname')
    dropdown_varibles1 = Profile.objects.all()
    dropdown_varibles2 = Profile.objects.filter(type_code='Worker').values_list('staff_id', 'staff_fname', 'staff_lname')
    dropdown = ['Error'] * len(dropdown_varibles)
    dropdownst = ['Error'] * len(dropdown_varibles2)
    for i in dropdown_varibles:
        dropdown[counter] = 'CID(' + str(i[0]) + ')' + ' ' + i[1] + ', ' + i[2]
        counter += 1
    dropdown = json.dumps(list(dropdown))
    for i in dropdown_varibles2:
        dropdownst[counter2] = 'ID(' + str(i[0]) + ')' + ' ' + i[1] + ', ' + i[2]
        counter2 += 1
    dropdown2 = json.dumps(list(dropdownst))
    test = str(request)
    y = ''
    for x in test:
        if x.isnumeric():
            y = y + x
    if request.method == "POST":
        form = scedshiftform(request.POST)
        if 'getstaff' in request.POST['submit']:
            if form:
                # setting variables to avoid errors.
                dateerror = 0
                starterror = 0
                enderror = 0
                error = 0
                shiftdatae = ''
                shiftstart = ''
                shiftend = ''
                form.full_clean()
                supernum = form.cleaned_data["shift_super"]
                # The form is not verified due to this search requiring only 3 variables, Another form cloud be created
                # but this is quicker and will return fewer errors. These trys make sure the variables are set and
                # returns an error if not.
                try:
                    clientname = str(form.cleaned_data["client_id"])
                except KeyError:
                    clientname = ''
                try:
                    shiftnotes = form.cleaned_data["shift_notes"]
                except KeyError:
                    shiftnotes = ""
                try:
                    depart = form.cleaned_data["dep_code"]
                except KeyError:
                    depart = ""
                try:
                    cliid = form.cleaned_data["client_id"]
                except KeyError:
                    cliid = ""
                try:
                    shiftstart = form.cleaned_data["scheduled_start"]
                except KeyError as e:
                    error += 1
                    starterror = 1
                try:
                    shiftend = form.cleaned_data["scheduled_end"]
                except KeyError as e:
                    error += 1
                    enderror = 1
                # If there is an error a message is returned.
                if error > 0:
                    if starterror == 1:
                        shiftstart = ''
                    if enderror == 1:
                        shiftend = ''
                    form = scedshiftform(initial={'scheduled_start': shiftstart,
                                                  'scheduled_end': shiftend, 'client_id': clientname,
                                                  'shift_super': supernum, 'shift_notes': shiftnotes})
                    # This gets the department and returns nothing if nothing was set.
                    try:
                        quryval = Department.objects.filter(dep_code=depart).values_list('dep_name', flat=True)
                        progval = 'value=' + str(depart)
                        progval1 = str(quryval[0])
                    except IndexError:
                        progval = 'value='
                        progval1 = 'Select a Department:'
                    messages.warning(request, 'Make sure the start time and end time are filled out ',
                                     extra_tags='mor')
                    return render(request, 'schedule/modrecshift.html',
                                  {'staffis': 1, 'form': form, 'dep': getdep, 'dropdown': dropdown,
                                   'dropdown1': dropdown_varibles1,
                                   'state': False, 'startval': progval, 'startval1': progval1, 'dropdown2': dropdown2,
                                   'usertype': user_group})
                reccc = RecShift.objects.filter(pk=y).values_list('rec_day', flat=True)
                week = {'mon': 0, 'tue': 1, 'wed': 2, 'thu': 3, 'fri': 4,
                             'sat': 5, 'sun': 6}
                shiftday = week[reccc[0]]
                dayofweek = {0: 'mon_avail', 1: 'tue_avail', 2: 'wed_avail', 3: 'thu_avail', 4: 'fri_avail',
                             5: 'sat_avail', 6: 'sun_avail', }
                query = getdayofweek(shiftday)
                stafflist = query.values_list(dayofweek[shiftday], 'staff_id', 'staff_fname', 'staff_lname')
                count = 0
                # This finds avalible staff based on time and date
                avalablestaff = [''] * len(stafflist)
                for i in stafflist:
                    timelist = str(i[0]).split(' - ')
                    start = str(timelist[0]).split(':')
                    start = datetime.time(int(start[0]), int(start[1]))
                    end = str(timelist[1]).split(':')
                    end = datetime.time(int(end[0]), int(end[1]))
                    if shiftstart.hour <= start.hour and shiftend.hour >= end.hour:
                        avalablestaff[count] = [i[1], i[2], i[3]]
                        count += 1
            form = scedshiftform(initial={'scheduled_start': shiftstart,
                                          'scheduled_end': shiftend, 'client_id': cliid,
                                          'shift_super': supernum, 'shift_notes': shiftnotes})
            deparmenv = getdepartment(depart)
            # This will return an error message if there are no staff with the required specs.
            if not avalablestaff:
                messages.warning(request, 'No avalable staff for the given date/time', extra_tags='mor')
            return render(request, 'schedule/modrecshift.html',
                          {'staffis': 0, 'form': form, 'dep': getdep, 'dropdown': dropdown, 'dropdown1': avalablestaff,
                           'state': False, 'startval1': deparmenv[1], 'startval': deparmenv[0], 'dropdown2': dropdown2,
                           'usertype': user_group})
        if form:
            form.full_clean()
            cleaned = str(form.cleaned_data["client_id"]).split(' ')
            cleaned = cleaned[0].replace('CID(', '').replace(')', '')
            department = request.POST['dep_code']
            start = form.cleaned_data["scheduled_start"]
            end = form.cleaned_data["scheduled_end"]
            staff = request.POST['staff_id']
            supervisor = form.cleaned_data["shift_super"]
            notes = form.cleaned_data["shift_notes"]
            count3 = 0
            editshifts = Shift.objects.filter(rec_id=y).values_list('shift_id', flat=True)
            dates = Shift.objects.filter(rec_id=y).values_list('shift_date', flat=True)
            date = ['Error'] * len(dates)
            for i in dates:
                i = str(i)
                date[count3] = i
                count3 += 1
            startshift = Shift.objects.filter(rec_id=y).values_list('scheduled_start', flat=True).first()
            endshift = Shift.objects.filter(rec_id=y).values_list('scheduled_end', flat=True).first()
            recovererr = recovertime(staff, dates, startshift, endshift, request.POST['submit'])
            if recovererr[0]:
                err = 1
                overtime = 1
                msg = messages.warning(request, f'The worker will work overtime for {recovererr[1]} shifts', extra_tags='error')
            reccliover = rechours(date, cleaned, startshift, endshift)
            if len(reccliover) != 0:
                err = 1
                msg = messages.warning(request, 'The client is over there monthy hours', extra_tags='error')
            recinter = recintersection(dates, cleaned, staff, startshift, endshift, y)
            if recinter[0]:
                err = 1
                messages.warning(request, recinter[1], extra_tags='error')
            if err == 1:
                form = scedshiftform(initial={'scheduled_start': start,
                                              'scheduled_end': end, 'client_id': getclient(cleaned),
                                              'shift_super': supervisor, 'shift_notes': notes})
                deparmenv = getdepartment(department)
                staffreturn = getstaff(staff)
                msg
                return render(request, "schedule/modrecshift.html",
                              {'staffis': 1, 'form': form, 'dep': getdep, 'dropdown': dropdown,
                               'dropdown1': dropdown_varibles1,
                               'state': True, 'startval1': deparmenv[1], 'startval': deparmenv[0],
                               'staffval': staffreturn[0], 'staffval1': staffreturn[1], 'overtime': 1,
                               'dropdown2': dropdown2, 'overtime': overtime, 'usertype': user_group})
            RecShift.objects.filter(pk=y).update(client_id=cleaned, staff_id=staff, dep_code=department,
                                                 rec_start=start, rec_end=end, rec_super=supervisor, rec_notes=notes)
            for i in editshifts:
                date = Shift.objects.filter(shift_id=i).values_list('shift_date', flat=True)
                now = datetime.now()
                if now.date() >= date[0] and now.time() >= start:
                    youerr = 1
                    continue
                Shift.objects.filter(pk=i).update(client_id=cleaned, dep_code=department,
                                                  scheduled_start=start, scheduled_end=end, staff_id=staff,
                                                  shift_super=supervisor, shift_notes=notes)
            if youerr == 1:
                messages.success(request, 'Shift records have been updated. Some'
                                          ' recodrds have been worked and can not be edited', extra_tags='submit')
            else:
                messages.success(request, 'Shift records have been updated', extra_tags='submit')
            return redirect('/viewrecshift')

    recshiftinfo = RecShift.objects.filter(rec_id=y)
    for i in recshiftinfo:
        cli = getclient(i.client_id)
        form = scedshiftform(
            initial={'client_id': cli,
                     'scheduled_start': i.rec_start,
                     'scheduled_end': i.rec_end, 'shift_super': i.rec_super,
                     'shift_notes': i.rec_notes})
        day = i.rec_day
        now = datetime.now()
        valsuper = i.rec_super
        staffreturn = getstaff(i.staff_id)
        redep = str(i.dep_code).replace('Department object (', '').replace(')', '')
        progval = getdepartment(redep)
        return render(request, "schedule/modrecshift.html",
                      {'usergroup': user_group, 'form': form, 'dropdown': dropdown, 'dropdown1': dropdown_varibles1,
                       'dropdown2': dropdown2, 'dep': getdep, 'staffis': 1, 'staffval': staffreturn[0],
                       'staffval1': staffreturn[1], 'startval': progval[0], 'startval1': progval[1],
                       'super': valsuper, 'day': day, 'usertype': user_group})

@login_required
@allowed_users(allowed_roles=['Coordinator', 'Bookeeper'])
def approvehours(request):
    user_group = request.user.groups.values_list('name', flat=True)
    user_group = str(user_group[0])

    nums = ''
    empty = 0
    people = Shift.objects.filter(status_code='Claimed').values_list('staff_id', flat=True)
    if len(people) == 0:
        empty = 1
    people = list(dict.fromkeys(people))
    aprove = approvesheet(people)
    return render(request, "schedule/aprovehours.html", {'sheet': aprove, 'empty': empty, 'usertype': user_group})


@login_required
@allowed_users1(allowed_roles=['Coordinator', 'Bookeeper'])
def approve(request):
    user_group = request.user.groups.values_list('name', flat=True)
    user_group = str(user_group[0])

    test = str(request)
    y = ''
    empty = 0
    for x in test:
        if x.isnumeric():
            y = y + x
    if request.method == "POST":
        check = 0
        for i in request.POST:
            if check == 1:
                sfg = str(i).split('-')
                if sfg[0] == bp and sfg[1] == 'en':
                    Shift.objects.filter(pk=bp).update(status_code='Approved', approved_start=request.POST[str(bp + '-st')], approved_end=request.POST[str(bp + '-en')])
                    check = 0
            shg = str(i).split('-')
            if len(shg) == 1:
                continue
            if shg[1] == 'st':
                if len(request.POST[i]) != 0:
                    check = 1
                    bp = shg[0]

    worker = Profile.objects.filter(pk=y).values_list('staff_fname', 'staff_lname')
    name = str(worker[0][0]) + ', ' + str(worker[0][1])
    shifts = Shift.objects.filter(status_code='Claimed', staff_id=y)
    if len(shifts) == 0:
        empty = 1
    sheet = submithours(shifts, name, y)
    return render(request, "schedule/approve.html", {'name': name, 'sheet': sheet, 'id': y, 'empty': empty, 'usertype': user_group})

@login_required
@allowed_users(allowed_roles=['Coordinator', 'Bookeeper'])
def reports(request):
    user_group = request.user.groups.values_list('name', flat=True)
    user_group = str(user_group[0])

    def year():
        dates = ['Error'] * 30
        today = date.today()
        count = 0
        year = int(today.year)
        for i in range(30):
            dates[count] = year
            count += 1
            year -= 1
        return dates
    sheet = ''
    startmonth = ''
    startyear = ''
    dates = ''
    switch = ''
    sname = ''
    dismonth = ''
    disyear = ''
    dropdown = ''
    disswitch = ''
    mname = ''
    staffname = ''
    if request.method == "POST":
        dates = year()
        startmonth = request.POST['month']
        startyear = request.POST['year']
        switch = request.POST['switch']
        staffname = request.POST['staffname']
        if request.POST['month'] == '':
            messages.warning(request, 'Make sure the month is entered')
            if request.POST['switch'] == 'half1':
                sname = '1-15'
            if request.POST['switch'] == 'half2':
                sname = '16-end'
            if request.POST['switch'] == 'full':
                sname = 'full'
            disyear = '''<option hidden value="''' + request.POST['year'] + '''">''' + request.POST['year'] + '</option>'
            disswitch = '''<option hidden value="''' + request.POST['switch'] + '''">''' + sname + '</option>'
            return render(request, "schedule/report.html", {'sheet': sheet, 'start': startmonth, 'end': startyear, 'year': dates, 'yearback': disyear, 'switchback': disswitch, 'usertype': user_group})
        if request.POST['switch'] == '':
            messages.warning(request, 'Make sure the span is entered')
            mname = monthword(request.POST['month'])
            dismonth = '''<option hidden value="''' + request.POST['month'] + '''">''' + mname + '</option>'
            disyear = '''<option hidden value="''' + request.POST['year'] + '''">''' + request.POST['year'] + '</option>'
            return render(request, "schedule/report.html", {'sheet': sheet, 'start': startmonth, 'end': startyear, 'year': dates, 'yearback': disyear, 'monthback': dismonth,'usertype': user_group})
        try:
            staffname = request.POST['staffname']
            staffname = str(staffname).split(' ')
            staffname = staffname[0].replace('ID(', '').replace(')', '')
            staffname = int(staffname)
        except:
            staffname = ''
        sheet = makereport(startmonth, startyear, switch, staffname)
        namess = stafflist(switch, startyear, startmonth)
        dropdown_varibles = Profile.objects.filter(staff_id__in=namess).values_list('staff_id', 'staff_fname', 'staff_lname')
        dropdown = ['Error'] * len(dropdown_varibles)
        counter = 0
        for i in dropdown_varibles:
            dropdown[counter] = 'ID(' + str(i[0]) + ')' + ' ' + i[1] + ', ' + i[2]
            counter += 1
        dropdown = json.dumps(list(dropdown))
    try:
        switch = request.POST['switch']
    except django.utils.datastructures.MultiValueDictKeyError:
        switch = None
    if switch == 'half1':
        sname = '1-15'
    if switch == 'half2':
        sname = '16-end'
    if switch == 'full':
        sname = 'full'
    try:
        mname = monthword(request.POST['month'])
    except django.utils.datastructures.MultiValueDictKeyError:
        mname = None
    try:
        dismonth = '''<option hidden value="''' + request.POST['month'] + '''">''' + mname + '</option>'
    except django.utils.datastructures.MultiValueDictKeyError:
        dismonth = None
    try:
        disyear = '''<option hidden value="''' + request.POST['year'] + '''">''' + request.POST['year'] + '</option>'
    except django.utils.datastructures.MultiValueDictKeyError:
        disyear = None
    try:
        disswitch = '''<option hidden value="''' + request.POST['switch'] + '''">''' + sname + '</option>'
    except django.utils.datastructures.MultiValueDictKeyError:
        disswitch = None
    dates = year()
    return render(request, "schedule/report.html", {'usertype': user_group, 'dropdown': dropdown, 'sheet': sheet, 'start': startmonth, 'end': startyear, 'year': dates, 'yearback': disyear, 'monthback': dismonth, 'switchback': disswitch})
